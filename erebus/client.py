from asyncio import AbstractEventLoop, get_event_loop
from traceback import print_exception
from typing import Optional

from .events import EventListener, maybe_await
from .flags import Intents
from .gateway import GatewayWebSocket
from .guild import Guild
from .message import Message
from .rest import Rest

class Client:
    def __init__(
        self,
        *,
        loop: Optional[AbstractEventLoop] = None,
        token: Optional[str] = None,
        is_bot: Optional[bool] = None,
        intents: Optional[Intents] = None
    ):
        self.token = token
        self.loop = loop or get_event_loop()
        self.ws = GatewayWebSocket(self)
        self.rest = Rest(self)
        self.is_bot = is_bot
        self.logged_in = False
        self._listeners = []
        self.intents = intents or Intents.without_privileged()
        self.guilds = {}
        self.channels = {}
        self.messages = {}
    
    async def login(self, token: Optional[str] = None) -> None:
        if token is None:
            if self.token is None:
                raise ValueError("A token wasn't passed.")
        else:
            self.token = token

        await self.rest.login()
        self.logged_in = True
    
    async def connect(self):
        if not self.logged_in:
            raise Exception("Cannot connect to websocket without logging in.")
        socket = await self.rest.ws_connect()
        try:
            await self.ws.connect(socket)
        except KeyboardInterrupt:
            pass
        finally:
            await self.rest._session.close()
    
    async def start(self, *args, **kwargs):
        await self.login(*args, **kwargs)
        await self.connect()
    
    def run(self, *args, **kwargs):
        self.loop.run_until_complete(self.start(*args, **kwargs))
        self.loop.close()
    
    async def dispatch_event(self, event_name: str, *args, **kwargs):
        for listener in filter(lambda l: l.event_name == event_name, self._listeners):
            await listener(*args, **kwargs)

        listener = getattr(self, 'on_' + event_name, None)
        if listener is not None:
            await maybe_await(listener, *args, **kwargs)

    def add_listener(self, listener: EventListener):
        self._listeners.append(listener)
    
    def listener(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            listener = EventListener(func, func.__name__)
            self.add_listener(listener)
            return listener

        def deco(func):
            event_name = kwargs.get('event_name', kwargs.get('name', func.__name__))
            name = func.__name__ if not func.__name__.startswith('on_') else func.__name__[3:]
            listener = EventListener(func, event_name=event_name or name, check=kwargs.get('check'))
            self.add_listener(listener)
            return listener

        return deco

    def on(self, event_name: str):
        def deco(func):
            listener = EventListener(func, event_name=event_name)
            self.add_listener(listener)
            return listener
        return deco
    


    async def _handle_message_create(self, event_name: str, data: dict):
        msg = Message._create_message(self, data)
        await self.dispatch_event(event_name, msg)

    async def _handle_guild_create(self, event_name: str, data: dict):
        guild = Guild._create_guild(data)
        self.guilds[guild.id] = guild
        await self.dispatch_event(event_name, guild)

    def on_error(self, error: Exception):
        if 'error' not in (listener.event_name for listener in self._listeners):
            print_exception(type(error), error, error.__traceback__)

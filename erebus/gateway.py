from aiohttp import ClientWebSocketResponse, WSMsgType
import asyncio
from json import loads
import sys
from typing import TYPE_CHECKING

from .enums import DiscordOpcode, Intents

class GatewayWebSocket:
    def __init__(self, client) -> None:
        self.client = client
        self.socket = self.seq = self._keep_alive_task = None
        self._keeping_alive = False
    
    async def connect(self, socket: ClientWebSocketResponse) -> None:
        self.socket = socket
        msg = await socket.receive()
        await self._handle_message(msg)

        await self.identify()
        while True:
            msg = await self.socket.receive()

            if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.closing):
                return
            elif msg.type is WSMsgType.ERROR:
                raise msg.data
            
            await self._handle_message(msg)
        
    async def _handle_message(self, msg):
        msg = loads(msg.data)
        op = msg.get('op')
        data = msg.get('d')
        seq = msg.get('s')

        if seq:
            self.seq = seq
        
        if op == DiscordOpcode.HELLO:
            await self.send_heartbeat()
            self.heartbeat_interval = data['heartbeat_interval'] / 1000
            self._keep_alive_task = asyncio.create_task(self._keep_alive())
        
        elif op in (DiscordOpcode.INVALID_SESSION, DiscordOpcode.RECONNECT):
            await self.close()
        
        elif op == DiscordOpcode.HEARTBEAT:
            await self.send_heartbeat()
        
        if op != DiscordOpcode.DISPATCH:
            return
        
        event = msg['t']

        if event == 'READY':
            self.session_id = data['session_id']
            return await self.client.dispatch_event('ready')

        handler = getattr(self.client, f'_handle_{event.lower()}', self.client.dispatch_event)

        try:
            await handler(event.lower(), data)
        except Exception as e:
            await self.client.dispatch_event('error', e)
        
    

    async def _keep_alive(self) -> None:
        while not await asyncio.sleep(self.heartbeat_interval):
            await self.send_heartbeat()

    async def send_heartbeat(self) -> None:
        payload = {
            'op': DiscordOpcode.HEARTBEAT,
            'd': self.seq 
        }
        await self.socket.send_json(payload)

        

    async def identify(self) -> None:
        payload = {
            'op': DiscordOpcode.IDENTIFY,
            'd': {
                'token': self.client.token,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'discord-api-py',
                    '$device': 'discord-api-py',
                    '$referrer': '',
                    '$referring_domain': ''
                },
                'compress': False,
                'large_threshold': 250,
                'guild_subscriptions': True,
                'v': 3
            }
        }

        payload['d']['intents'] = self.client.intents.value
        await self.socket.send_json(payload)
    
    async def close(self, code: int = 1000) -> None:
        if self._keep_alive_task is not None:
            self._keep_alive_task.cancel()
        await self.socket.close(code=code)
    
import sys
from typing import Optional
from asyncio import iscoroutine

if sys.version_info >= (3, 9):
    from collections.abc import Callable
else:
    from typing import Callable

async def maybe_await(func: Callable, *args, **kwargs):
    ret = func(*args, **kwargs)
    return await ret if iscoroutine(ret) else ret

class EventListener:
    def __init__(self, callback: Callable, *, event_name: str, check: Optional[Callable[..., bool]] = None) -> None:
        if check is None:
            check = lambda *args, **kwargs: True
        self.check = check
        self.event_name = event_name
        self.callback = callback
    
    async def call(self, *args, **kwargs) -> None:
        ret = await maybe_await(self.check, *args, **kwargs)   
        if ret:
            return await maybe_await(self.callback, *args, **kwargs)

    __call__ = call



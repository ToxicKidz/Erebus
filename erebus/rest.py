from aiohttp import ClientSession, ContentTypeError
from functools import partialmethod
from typing import Any, Dict, List, Optional, Union

from . import __version__


API_BASE_URL = "https://discord.com/api/v8"

def get_api_url(route: str):
    return API_BASE_URL + route

RequestResponse = Union[dict, str]

class Rest:
    def __init__(self, client):
        self._session = None
        self.token = None
        self.user_agent = f'DiscordBot (https://github.com/ToxicKidz/discord-api-py {__version__})'
        self.client = client
    
    async def request(self, method: str, url: str, **kwargs) -> RequestResponse:
        headers = {
            'User-Agent': self.user_agent,
            'X-Ratelimit-Precision': 'millisecond',
            'Authorization': 'Bot ' + self.client.token
        }

        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        async with self._session.request(method, url, headers=headers, **kwargs)  as response:
            response.raise_for_status()
            try:
                return await response.json()
            except ContentTypeError:
                return await response.text()
    
    get = partialmethod(request, 'GET')
    put = partialmethod(request, 'PUT')
    post = partialmethod(request, 'POST')
    patch = partialmethod(request, 'PATCH')
    delete = partialmethod(request, 'DELETE')
    
    async def login(self) -> RequestResponse:
        self._session = ClientSession()
        return await self.get(get_api_url('/users/@me'))
    
    async def logout(self) -> RequestResponse:
        return await self.get(get_api_url('/auth/logout'))
    
    async def get_gateway(self) -> RequestResponse:
        return await self.get(get_api_url('/gateway'))
    
    async def ws_connect(self):
        data = await self.get_gateway()
        return await self._session.ws_connect(data['url'] + '?v=8')

    async def get_audit_logs(
        self,
        guild_id: int,
        *,
        user_id: Optional[int] = None,
        action_type: Optional[int] = None,
        before: Optional[int] = None,
        limit: Optional[int] = None
    ) -> RequestResponse:
        params = {}

        if user_id is not None:
            params['user_id'] = user_id
        
        if action_type is not None:
            params['action_type'] = action_type
        
        if before is not None:
            params['before'] = before
        
        if limit is not None:
            params['limit'] = limit

        return await self.get(get_api_url(f'/guilds/{guild_id}/audit-logs'), params=params)

    async def create_message(
        self,
        channel_id,
        content=None,
        *,
        tts=False,
        embed=None,
        nonce=None,
        allowed_mentions=None,
        message_reference=None
    ):
        payload = {'tts': tts}

        if content:
            payload['content'] = content
        
        if embed:
            payload['embed'] = embed
        
        if nonce:
            payload['nonce'] = nonce
        
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        
        if message_reference:
            payload['message_reference'] = message_reference
        
        return await self.post(get_api_url(f'/channels/{channel_id}/messages'), json=payload)

    async def get_channel(self, channel_id: int):
        return await self.get(get_api_url(f'/channels/{channel_id}'))
    
    async def modify_channel(
        self,
        channel_id: int,
        *,
        name: Optional[str] = None,
        type: Optional[int] = None,
        position: Optional[int] = None,
        topic: Optional[str] = None,
        nsfw: Optional[bool] = None,
        rate_limit_per_user: Optional[int] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        permission_overwrites: Optional[list] = None,
        parent_id: Optional[int] = None
    ) -> RequestResponse:
        payload = {}

        if name is not None:
            payload['name'] = name
        
        if type is not None:
            payload['type'] = type
        
        if position is not None:
            payload['position'] = position
        
        if topic is not None:
            payload['topic'] = topic
        
        if nsfw is not None:
            payload['nsfw'] = nsfw
        
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user
        
        if bitrate is not None:
            payload['bitrate'] = bitrate
        
        if user_limit is not None:
            payload['user_limit'] = user_limit
        
        if permission_overwrites is not None:
            payload['permission_overwrites'] = permission_overwrites
        
        if parent_id is not None:
            payload['parent_id'] = parent_id
        
        return await self.patch(get_api_url(f'/channels/{channel_id}'), json=payload)

    async def delete_channel(self, channel_id: int) -> RequestResponse:
        return await self.delete(get_api_url(f'/channels/{channel_id}'))
    
    async def get_messages(
        self,
        channel_id: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
        around: Optional[int] = None,
    ) -> RequestResponse:
        
        params = {}

        if before is not None:
            params = {'before': before}
        elif after is not None:
            params = {'after': after}
        elif around is not None:
            params = {'around': around}

        return await self.get(get_api_url(f'/channels/{channel_id}/messages'), params=params)

    async def get_message(self, channel_id: int, message_id: int):
        return await self.get(get_api_url(f'/channels/{channel_id}/messages/{message_id}'))
    
    async def cross_post_message(self, channel_id: int, message_id: int):
        return await self.post(get_api_url(f'/channels/{channel_id}/messages/{message_id}'))

    async def create_reaction(self, channel_id: int, message_id: int, emoji: dict):
        return await self.put(get_api_url(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'))
    
    async def delete_reaction(self, channel_id: int, message_id: int, emoji: dict, user: Optional[int] = None):
        return await self.delete(
            get_api_url(f'channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user or "@me"}')
        )
    
    async def get_reactions( 
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        before: Optional[int] = None,
        after: Optional[int] = None,
        limit: Optional[int] = None
    ) -> RequestResponse:
        params = {}

        if before is not None:
            params['before'] = before

        if after is not None:
            params['after'] = after
        
        if limit is not None:
            params['limit'] = limit
        
        return await self.get(
            get_api_url(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'), params=params
        )
    
    async def clear_reactions(self, channel_id: int, message_id: int) -> RequestResponse:
        return await self.delete(get_api_url(f'channels/{channel_id}/messages/{message_id}/reactions'))

    async def clear_reaction(self, channel_id: int, message_id: int, emoji: dict) -> RequestResponse:
        return await self.delete(get_api_url(f'channels/{channel_id}/messages/{message_id}/reactions/{emoji}'))
    
    async def edit_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        content: Optional[str] = None,
        embed=None,
        allowed_mentions=None,
        flags=None
    ) -> RequestResponse:
        payload = {}

        if content is not None:
            payload['content'] = content

        if embed is not None:
            payload['embed'] = embed
        
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        
        if flags is not None:
            payload['flags'] = flags
        
        return await self.patch(get_api_url(f'/channels/{channel_id}/messages/{message_id}'), params=payload)

    async def delete_message(self, channel_id: int, message_id: int):
        return await self.delete(get_api_url(f'/channels/{channel_id}/message/{message_id}'))
    
    async def bulk_delete_messages(self, channel_id: int, messages: List[int]):
        return await self.post(get_api_url(f'/channels/{channel_id}/messages/bulk-delete'), json={'messages': messages})
    
    async def edit_channel_permissions(
        self,
        channel_id: int,
        overwrite_id: int,
        allow: str,
        deny: str,
        type: int
        ) -> RequestResponse:
        return await self.put(
            get_api_url(f'/channels/{channel_id}/permissions/{overwrite_id}'),
            json={'allow': allow, 'deny': deny, 'type': type}
        )
    
    async def get_channel_invites(self, channel_id: int) -> RequestResponse:
        return await self.get(get_api_url(f'/channels/{channel_id}/invites'))
    
    async def create_channel_invite(
        self,
        channel_id: int,
        max_age: int = 0,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        target_user: Optional[int] = None,
        target_user_type: Optional[int] = None
    ) -> RequestResponse:
        payload = {'max_age': max_age, 'max_uses': max_uses, 'temporary': temporary, 'unique': unique}

        if target_user is not None:
            payload['target_user'] = target_user
        
        if target_user_type is not None:
            payload['target_user_type'] = target_user_type
        
        return await self.post(get_api_url(f'/channels/{channel_id}/invites'), json=payload)
    
    async def delete_channel_permission(self, channel_id: int, overwrite_id: int):
        return await self.delete(get_api_url(f'/channels/{channel_id}/permissions/{overwrite_id}'))
    
    async def trigger_typing(self, channel_id: int):
        return await self.post(get_api_url(f'/channels/{channel_id}/typing'))
    
    async def get_pins(self, channel_id: int):
        return await self.get(get_api_url(f'/channels/{channel_id}/pins'))
    
    async def add_pin(self, channel_id: int, message_id: int):
        return await self.put(get_api_url(f'/channels/{channel_id}/pins/{message_id}'))

    async def delete_pin(self, channel_id: int, message_id: int):
        return await self.delete(get_api_url(f'/channels/{channel_id}/pins/{message_id}'))
    
    async def get_emojis(self, guild_id: int) -> RequestResponse:
        return await self.get(get_api_url(f'/guilds/{guild_id}/emojis'))

    async def get_emoji(self, guild_id: int, emoji_id: int) -> RequestResponse:
        return await self.get(get_api_url(f'/guilds/{guild_id}/emojis/{emoji_id}')) 
    
    #TODO: Add create_emoji

    async def edit_emoji(
        self,
        guild_id: int,
        emoji_id: int,
        name: Optional[str] = None,
        roles: Optional[List[int]] = None
    ) -> RequestResponse:
        payload = {}

        if name is not None:
            payload['name'] = name
        
        if roles is not None:
            payload['roles'] = roles

        return await self.patch(get_api_url(f'/guilds/{guild_id}/emojis/{emoji_id}'), json=payload)
    
    async def delete_emoji(self, guild_id: int, emoji_id: int) -> RequestResponse:
        return await self.delete(get_api_url(f'/guilds/{guild_id}/emojis/{emoji_id}'))
    
    async def create_guild(
        self,
        *,
        name: str,
        region: Optional[str] = None,
        icon: Optional[str] = None,
        verification_level: Optional[int] = None,
        default_message_notifications: Optional[int] = None,
        expicit_content_filter: Optional[int] = None,
        roles: Optional[List[dict]] = None,
        channels: Optional[List[dict]] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[dict] = None,
        system_channel_id: Optional[int] = None
    ) -> RequestResponse:
        payload = {'name': name}

        if region is not None:
            payload['region'] = region

        if icon is not None:
            payload['icon'] = icon

        if verification_level is not None:
            payload['verification_level'] = verification_level

        if default_message_notifications is not None:
            payload['default_message_notifications'] = default_message_notifications

        if expicit_content_filter is not None:
            payload['expicit_content_filter'] = expicit_content_filter
        
        if roles is not None:
            payload['roles'] = roles
        
        if channels is not None:
            payload['channels'] = channels
        
        if afk_channel_id is not None:
            payload['afk_channel_id'] = afk_channel_id
        
        if afk_timeout is not None:
            payload['afk_timeout'] = afk_timeout

        if system_channel_id is not None:
            payload['system_channel_id'] = system_channel_id
        
        return await self.post(get_api_url('/guilds'), json=payload)
    
    async def get_guild(self, guild_id: int) -> RequestResponse:
        return await self.get(get_api_url(f'/guilds/{guild_id}'))
    
    async def get_guild_preview(self, guild_id: int):
        return await self.get(get_api_url(f'guilds/{guild_id}/preview'))

    async def edit_guild(
        self,
        *,
        name: Optional[str] = None,
        region: Optional[str] = None,
        icon: Optional[str] = None,
        verification_level: Optional[int] = None,
        default_message_notifications: Optional[int] = None,
        expicit_content_filter: Optional[int] = None,
        roles: Optional[List[dict]] = None,
        channels: Optional[List[dict]] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[dict] = None,
        system_channel_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        splash: Optional[str] = None,
        banner: Optional[str] = None,
        rules_channel_id: Optional[int] = None,
        public_updates_channel_id: Optional[int] = None,
        preferred_locale: Optional[str] = None
    ) -> RequestResponse:
        payload = {}

        payload = {}

        if name is not None:
            payload['name'] = name

        if region is not None:
            payload['region'] = region

        if icon is not None:
            payload['icon'] = icon

        if verification_level is not None:
            payload['verification_level'] = verification_level

        if default_message_notifications is not None:
            payload['default_message_notifications'] = default_message_notifications

        if expicit_content_filter is not None:
            payload['expicit_content_filter'] = expicit_content_filter
        
        if roles is not None:
            payload['roles'] = roles
        
        if channels is not None:
            payload['channels'] = channels
        
        if afk_channel_id is not None:
            payload['afk_channel_id'] = afk_channel_id
        
        if afk_timeout is not None:
            payload['afk_timeout'] = afk_timeout

        if system_channel_id is not None:
            payload['system_channel_id'] = system_channel_id

        if owner_id is not None:
            payload['owner_id'] = owner_id
        
        if splash is not None:
            payload['splash'] = splash
        
        if banner is not None:
            payload['banner'] = banner
        
        if rules_channel_id is not None:
            payload['rules_channel_id'] = rules_channel_id

        if public_updates_channel_id is not None:
            payload['public_updates_channel_id'] = public_updates_channel_id
        
        if preferred_locale is not None:
            payload['preferred_locale'] = preferred_locale
        
        return await self.patch(get_api_url('/guilds'), json=payload)

    async def delete_guild(self, guild_id: int) -> RequestResponse:
        return await self.delete(get_api_url(f'/guilds/{guild_id}'))

    async def create_guild_channel(
        self,
        guild_id: int,
        *,
        name: str,
        type: Optional[int] = None,
        topic: Optional[str] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[Dict['str', Any]]] = None,
        parent_id: Optional[int],
        nsfw: Optional[bool] = None
    ) -> RequestResponse:
        payload = {'name': name}

        if type is not None:
            payload['type'] = type
        
        if topic is not None:
            payload['topic'] = topic
        
        if bitrate is not None:
            payload['bitrate'] = bitrate
        
        if user_limit is not None:
            payload['user_limit'] = bitrate
        
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user
        
        if position is not None:
            payload['position'] = position
        
        if permission_overwrites is not None:
            payload['permission_overwrites'] = permission_overwrites
        
        if parent_id is not None:
            payload['parent_id'] = parent_id
        
        if nsfw is not None:
            payload['nsfw'] = nsfw
        
        return await self.post(get_api_url(f'/guilds/{guild_id}/channels'), json=payload)
    
    async def modify_channel_position(self, guild_id: int, channel_id: int, position: Optional[int]):
        return await self.patch(get_api_url(f'/guilds/{guild_id}/channels'), json={'id': channel_id, 'position': position})

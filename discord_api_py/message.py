from datetime import datetime

class Message:
    __slots__ = ('type', 'tts', 'created', 'referenced_message', 'pinned', 'nonce', 'mentions', 'mention_roles',
                'author', 'attachments', 'guild', 'content', 'mention_channel', 'id', 'mention_everyone',
                'edited', 'embeds', 'flags', 'channel')
    
    def __new__(cls):
        raise Exception("Messages should not be created manually.") # TODO: Make exceptions

    @classmethod
    def _create_message(cls, client, data: dict):
        message = object.__new__(cls)
        message.id = data.get('id')
        message.type = data.get('type')
        message.tts = data.get('tts')
        message.created = data.get('timestamp')
        message.referenced_message = data.get('referenced_message')
        message.edited = data.get('edited_timestamp')
        message.mention_everyone = data.get('mention_everyone')
        message.guild = client.guilds.get(data.get('guild_id'))
        message.author = data.get('author')
        message.channel = data.get('channel_id')
        message.content = data.get('content')
        client.messages[message.id] = message
        return message

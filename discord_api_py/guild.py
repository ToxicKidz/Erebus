class Guild:
    __slots__ = ('id', 'name', 'icon', 'owner', 'client_is_owner', 'permissions', 'region', 'afk_channel',
                'afk_timeout', 'verification_level', 'roles', 'emojis', 'system_channel', 'features',
                'mfa_level', 'created', 'large', 'member_count', 'voice_states', 'members', 'channels',
                'max_members', 'vanity_url_code', 'description', 'banner',
                'premium_tier', 'premium_subscription_count')
    
    def __new__(cls):
        raise Exception('Guilds should not be created manually.')

    @classmethod
    def _create_guild(cls, data: dict):
        guild = object.__new__(cls)
        guild.id = data.get('id')
        guild.name = data.get('name')
        guild.icon = data.get('icon')
        guild.owner = data.get('owner_id')
        guild.client_is_owner = data.get('owner')
        guild.permissions = data.get('permissions')
        guild.members = data.get('members')
        guild.region = data.get('region')
        guild.afk_channel = data.get('afk_channel_id')
        guild.afk_timeout = data.get('afk_timeout')
        guild.verification_level = data.get('verification_level')
        guild.roles = data.get('roles')
        guild.emojis = data.get('emojis')
        guild.features = data.get('features')
        guild.mfa_level = data.get('mfa_level')
        guild.created = data.get('joined_at')
        guild.large = data.get('large')
        guild.member_count = data.get('member_count')
        guild.voice_states = data.get('voice_states')
        guild.channels = data.get('channels')
        guild.max_members = data.get('max_members')
        guild.vanity_url_code = data.get('vanity_code_url')
        guild.description = data.get('description')
        guild.banner = data.get('banner')
        guild.premium_tier = data.get('premium_tier')
        guild.premium_subscription_count = data.get('premium_subscription_count')
        return guild

from __future__ import annotations

from enum import Flag as EnumFlag
from typing import Optional, Type, Union

from .enums import Intents, MessageFlags as _MessageFlags

class Flag:

    def __init__(self, value: int) -> None:
        self.value = value

    def __get__(self, instance: Optional[BaseFlag], owner: Type[BaseFlag]) -> Union[Flag, bool]:
        if instance is None:
            return self
        return instance.value & self.value == self.value
    
    def __set__(self, instance: BaseFlag, value: bool) -> None:
        if value:
            instance.value |= self.value
        else:
            instance.value &= ~self.value

class FlagAlias:
    def __init__(self, *flags: EnumFlag) -> None:
        self.flags = flags
    
    def __set__(self, instance: BaseFlag, value: bool) -> None:
        for flag in self.flags:
            setattr(instance, flag.name.lower(), value)
    
    def __get__(self, instance: Optional[BaseFlag], owner: Type[BaseFlag]):
        if instance is None:
            return self
        return all(getattr(instance, flag.name.lower()) for flag in self.flags)

class BaseFlag:
    value = 0 # This is the default value for flags

    def __init_subclass__(cls, flag_cls: Type[EnumFlag]) -> None:
        cls.flag_names = []

        for flag in flag_cls:
            setattr(cls, flag.name.lower(), Flag(flag.value))
            cls.flag_names.append(flag.name.lower())
        

        cls.flag_aliases = [(name, attr) for name, attr in vars(cls).items() if isinstance(attr, FlagAlias)]
        cls.flag_alias_names = [name for name, attr in cls.flag_aliases]

    
    def __init__(self, **flags: bool) -> None:
        for flag, value in flags.items():
            if flag in self.flag_names + self.flag_alias_names:
                setattr(self, flag, value)
            else:
                raise ValueError(f"{flag!r} is not a valid flag name for {self.__class__.__name__!r}.")

    def __eq__(self, other: BaseFlag) -> bool:
        return hasattr(other, 'value') and self.value == other.value

    @classmethod
    def _from_value(cls, value: Optional[int]):
        if value is None:
            return value

        self = cls()
        setattr(self, 'value', value)

class Intents(BaseFlag, flag_cls=Intents):
    members = FlagAlias(Intents.GUILD_MEMBERS) # Let's just shorten the `guild_` prefix 
    bans = FlagAlias(Intents.GUILD_BANS)
    emojis = FlagAlias(Intents.GUILD_EMOJIS)
    integrations = FlagAlias(Intents.GUILD_INTEGRATIONS)
    webhooks = FlagAlias(Intents.GUILD_WEBHOOKS)
    invites = FlagAlias(Intents.GUILD_INVITES)
    voice_states = FlagAlias(Intents.GUILD_VOICE_STATES)
    presences = FlagAlias(Intents.GUILD_PRESENCES)

    messages = FlagAlias(Intents.GUILD_MESSAGES, Intents.DIRECT_MESSAGES) # Now group `DM` and `Guild` together
    reactions = FlagAlias(Intents.GUILD_MESSAGE_REACTIONS, Intents.DIRECT_MESSAGE_REACTIONS)
    typing = FlagAlias(Intents.GUILD_MESSAGE_TYPING, Intents.DIRECT_MESSAGE_TYPING)

    @classmethod
    def all(cls) -> Intents:
        return cls(**{name: True for name in cls.flag_names})
    
    @classmethod
    def none(cls) -> Intents:
        return cls()
    
    @classmethod
    def without_privileged(cls) -> Intents:
        intents = cls.all()
        intents.members = False
        intents.presences = False
        return intents

class MessageFlags(BaseFlag, enum=_MessageFlags):
    pass

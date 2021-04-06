from datetime import datetime

DISCORD_EPOCH = 1420070400000

def slowflake_to_datetime(id: int):
    return datetime.utcfromtimestamp(((id >> 22) + DISCORD_EPOCH) / 1000)

def datetime_to_snowflake(date_time: datetime):
    unix_seconds = (date_time - datetime(1970, 1, 1)).total_seconds()
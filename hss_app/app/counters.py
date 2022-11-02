import redis

from config import Config


class CounterDB(redis.Redis):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def incr(self, name, amount=1):
        try:
            super().incr(name, amount)
        except Exception as e:
            return None

    def decr(self, name, amount=1):
        try:
            super().decr(name, amount)
        except Exception as e:
            return None

    def get(self, name):
        try:
            return super().get(name)
        except Exception as e:
            return None


app_counterdb = CounterDB(host=Config.cache_ip_address, password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81", socket_connect_timeout=2)
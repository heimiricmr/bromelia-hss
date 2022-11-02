import redis


class CounterDB(redis.Redis):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)

    def incr(self, name, amount=1):
        try:
            return super().incr(name, amount)
        except:
            return None
        

app_counterdb = CounterDB(password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81")
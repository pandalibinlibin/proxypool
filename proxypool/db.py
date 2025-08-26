import redis
import random
from .setting import Setting


class RedisClient:
    def __init__(self, host=Setting.REDIS_HOST, port=Setting.REDIS_PORT, password=Setting.REDIS_PASSWORD):
        """
        Initialize the Redis client and create a connection.

        :param host: Redis server host address, default is REDIS_HOST
        :param port: Redis server port, default is REDIS_PORT
        :param password: Redis server password, default is REDIS_PASSWORD
        """
        self.db = redis.StrictRedis(
            host=host, port=port, password=password, decode_responses=True
        )

    def add(self, proxy, score=Setting.INITIAL_SCORE):
        """
        Add a proxy to Redis and set its score.

        :param proxy: The proxy to be added
        :param score: The score of the proxy, default is INITIAL_SCORE
        :return: The number of elements added to the sorted set, with duplicates ignored
        """
        if not self.db.zscore(Setting.REDIS_KEY, proxy):
            return self.db.zadd(Setting.REDIS_KEY, {proxy: score})

    def random(self):
        """
        Randomly get a high-score proxy.
        First try to randomly select one from proxies with MAX_SCORE.
        If none available, select from the suboptimal ones.
        Raise an exception if the pool is empty.

        :return: A randomly selected proxy
        """
        # Try to get proxies with MAX_SCORE
        proxies = self.db.zrangebyscore(Setting.REDIS_KEY, Setting.MAX_SCORE, Setting.MAX_SCORE)
        if proxies:
            return random.choice(proxies)

        # If no MAX_SCORE proxies, get all non-empty proxies in descending order of score
        proxies = self.db.zrevrange(Setting.REDIS_KEY, 0, -1)
        if proxies:
            return random.choice(proxies)

        # If pool is empty, raise an exception
        raise Exception("Proxy pool is empty")

    def decrease(self, proxy):
        """
        Decrease the score of a proxy by 1 when the proxy check fails.
        If the score is lower than MIN_SCORE, delete the proxy directly.

        :param proxy: The proxy whose score needs to be decreased
        :return: The new score of the proxy if it still exists, None if deleted
        """
        score = self.db.zscore(Setting.REDIS_KEY, proxy)
        if score is None:
            return None
        new_score = score - 1
        if new_score < MIN_SCORE:
            return self.db.zrem(Setting.REDIS_KEY, proxy)
        return self.db.zadd(Setting.REDIS_KEY, {proxy: new_score})

    def exists(self, proxy):
        """
        Check if a proxy exists in Redis.

        :param proxy: The proxy to be checked
        :return: True if the proxy exists, False otherwise
        """
        return self.db.zscore(Setting.REDIS_KEY, proxy) is not None

    def max(self, proxy):
        """
        Set the score of a proxy to the maximum value (used for high-quality proxies).

        :param proxy: The proxy whose score needs to be set to the maximum
        :return: The number of elements added to the sorted set, with duplicates ignored
        """
        return self.db.zadd(Setting.REDIS_KEY, {proxy: Setting.MAX_SCORE})

    def count(self):
        """
        Return the total number of proxies in the proxy pool.

        :return: The total number of proxies
        """
        return self.db.zcard(Setting.REDIS_KEY)

    def all(self):
        """
        Get a list of all proxies with scores between MIN_SCORE and MAX_SCORE.

        :return: A list of proxies
        """
        return self.db.zrangebyscore(Setting.REDIS_KEY, Setting.MIN_SCORE, Setting.MAX_SCORE)

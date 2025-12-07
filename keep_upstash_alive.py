from upstash_redis import Redis

redis = Redis.from_env()
response = redis.zscore('leaderboard', 'SupKittyMeow')

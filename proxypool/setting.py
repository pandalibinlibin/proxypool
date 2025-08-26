class Setting:
    # 代理评分相关常量
    MAX_SCORE = 100
    MIN_SCORE = 0
    INITIAL_SCORE = 10

    # Redis相关配置
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_KEY = "proxies"

    # 测试相关配置
    TEST_URL = "https://www.baidu.com"
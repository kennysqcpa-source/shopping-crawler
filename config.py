"""
爬虫配置文件
"""

# ============ 搜索配置 ============
KEYWORDS = ["厨房用品"]  # 搜索关键字列表

PAGES = 5  # 爬取前5页

# ============ 网站配置 ============
# 虾皮配置
SHOPEE_BASE_URL = "https://shopee.tw"
SHOPEE_SEARCH_URL = "https://shopee.tw/search"

# 亚马逊配置
AMAZON_BASE_URL = "https://www.amazon.com"
AMAZON_SEARCH_URL = "https://www.amazon.com/s"

# ============ 爬虫配置 ============
REQUEST_DELAY = 2  # 请求间隔（秒）
TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# ============ 数据库配置 ============
DB_PATH = "data/products.db"

# ============ 日志配置 ============
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/crawler.log"

# ============ 定时更新配置 ============
UPDATE_INTERVAL = 24  # 更新间隔（小时）
AUTO_UPDATE_ENABLED = False  # 是否启用自动更新

# ============ 代理配置（可选）============
USE_PROXY = False
PROXIES = {
    # "http": "http://proxy.example.com:8080",
    # "https": "http://proxy.example.com:8080",
}

# ============ Selenium 配置（用于动态网页）============
USE_SELENIUM = True  # 是否使用 Selenium
HEADLESS = True  # 无头浏览器模式

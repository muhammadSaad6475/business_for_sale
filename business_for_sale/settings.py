# Scrapy settings for business_for_sale project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "business_for_sale"

SPIDER_MODULES = ["business_for_sale.spiders"]
NEWSPIDER_MODULE = "business_for_sale.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "business_for_sale (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': '_gcl_au=1.1.133050538.1719123534; _gid=GA1.2.653889409.1719123534; _fbp=fb.1.1719123536133.630606850734819997; OptanonAlertBoxClosed=2024-06-23T06:19:31.950Z; ASP.NET_SessionId=2msrce0to5kzwkziztdk4lm3; lastSearch=C103:CategoryIds=310&FilterIds=&Keywords=&MoneyFrom=0&MoneyTo=10000000000&ReferrerSearchUrl=; _ga_4FE2DKM396=GS1.2.1719153484.5.0.1719153484.60.0.0; _clck=4xyck4%7C2%7Cfmw%7C0%7C1635; __gads=ID=3ca0d0a4e14b6c19:T=1719123536:RT=1719212643:S=ALNI_Mbz1AlPD-PC3CJ51TBe2mOju42p5g; __gpi=UID=00000e555380a5b8:T=1719123536:RT=1719212643:S=ALNI_MZOaL6cbZS3NoxjjsD1-Ftqe9d_lQ; __eoi=ID=bc8acda8711bda78:T=1719123536:RT=1719212643:S=AA-AfjZM1xPeE75pZdeXYgRT19DH; _ga_1G1NGBELLP=GS1.1.1719212638.5.1.1719212781.60.0.0; _ga=GA1.1.428301992.1719123533; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Jun+24+2024+12%3A06%3A21+GMT%2B0500+(Pakistan+Standard+Time)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&AwaitingReconsent=false&geolocation=PK%3BPB; _uetsid=76c98d40312811efba56fb975b55ff3d; _uetvid=76c9a7c0312811efbd87a79ee5bcbd18; _clsk=1rouy3r%7C1719213635720%7C5%7C1%7Cp.clarity.ms%2Fcollect; lastSearch=C103:CategoryIds=310&FilterIds=&Keywords=&MoneyFrom=0&MoneyTo=10000000000&ReferrerSearchUrl=',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "business_for_sale.middlewares.BusinessForSaleSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "business_for_sale.middlewares.BusinessForSaleDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "business_for_sale.pipelines.BusinessForSalePipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

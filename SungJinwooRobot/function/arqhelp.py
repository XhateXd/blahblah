import json
import sys
import aiohttp
from Python_ARQ import ARQ
aiohttpsession = aiohttp.ClientSession()
ARQ_API = get_str_key("ARQ_API", required=True)
ARQ_API_URL = "https://thearq.tech"
arq = ARQ(ARQ_API_URL, ARQ_API, aiohttpsession)

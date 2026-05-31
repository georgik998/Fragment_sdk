from typing import Literal
from tonutils.contracts.wallet import WalletV4R2, WalletV5R1
import json

FRAGMENT_BASE_URL: str = "https://fragment.com"

FRAGMENT_API_BASE_URL = 'https://fragment.com/api'
FRAGMENT_API_BASE_URL_WITH_PARAMS = 'https://fragment.com/api?hash={hash}'

WALLET_CHAIN = "-239"

# Комиссия сети
MIN_TON_BALANCE = 0.025

BASE_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://fragment.com",
    "priority": "u=1, i",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    ),
    "x-requested-with": "XMLHttpRequest",
}

DEVICE_HEADERS: str = json.dumps(
    {
        "platform": "iphone",
        "appName": "Tonkeeper",
        "appVersion": "5.5.2",
        "maxProtocolVersion": 2,
        "features": [
            "SendTransaction",
            {"name": "SendTransaction", "maxMessages": 255},
            {"name": "SignData", "types": ["text", "binary", "cell"]},
        ],
    }
)
WALLET_VERSION_TYPE = Literal['V4R2', 'V5R1']
DEFAULT_WALLET_VERSION: WALLET_VERSION_TYPE = 'V5R1'
WALLET_VERSION_DICT = {
    'V4R2': WalletV4R2,
    'V5R1': WalletV5R1
}

FRAGMENT_PAYMENT_METHOD_TYPE = Literal[
    'ton',
    'usdt_eth', 'usdt_pol', 'usdt_ton',
    'usdc_eth', 'usdc_pol', 'usdc_base'
]
DEFAULT_FRAGMENT_PAYMENT_METHOD: FRAGMENT_PAYMENT_METHOD_TYPE = 'ton'

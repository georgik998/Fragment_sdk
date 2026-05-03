import json

FRAGMENT_BASE_URL: str = "https://fragment.com"

FRAGMENT_API_BASE_URL = 'https://fragment.com/api?hash={hash}'


def get_fragment_api_base_url(_hash: str) -> str:
    return FRAGMENT_API_BASE_URL.format(hash=_hash)


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

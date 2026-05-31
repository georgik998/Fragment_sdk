from typing import Literal
from functools import wraps
import re

import httpx

from fragment_sdk.types.dto import BuyStarsDto
from fragment_sdk.types.exception import FragmentSdkExc
from fragment_sdk._clients.wallet import TonWalletClient
from fragment_sdk._clients.http import HttpClient
from fragment_sdk._methods.buy_stars import buy_stars
from fragment_sdk._methods.cookie import get_client_cookies
from fragment_sdk import const


class FragmentClient:
    account_info: dict = None
    http_client: HttpClient = None

    def __init__(
            self,
            api_key: str,
            seed: str,
            stel_ssid: str,
            stel_dt: str,
            stel_ton_token: str,
            stel_token: str,
            wallet_version: const.WALLET_VERSION_TYPE = const.DEFAULT_WALLET_VERSION,
            # payment_method: const.FRAGMENT_PAYMENT_METHOD_TYPE = const.DEFAULT_FRAGMENT_PAYMENT_METHOD
    ):
        self._api_key = api_key
        self._seed = seed
        self._cookies = {
            'stel_ssid': stel_ssid,
            'stel_dt': stel_dt,
            'stel_ton_token': stel_ton_token,
            'stel_token': stel_token
        }

        # Пока заглушка
        self.payment_method = 'ton'

        self.ton_wallet_client = TonWalletClient(
            api_key=self._api_key,
            seed=self._seed,
            version=wallet_version
        )

        self.__async_init = False

    @staticmethod
    def _require_init(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.__async_init is False:
                await self.async_init()
            return await func(self, *args, **kwargs)

        return wrapper

    async def async_init(self, headers=const.BASE_HEADERS):
        if self.__async_init is False:
            headers = {
                k: v
                for k, v in headers.items()
                if k not in ("accept", "accept-encoding", "content-type", "x-requested-with", "x-aj-referer")
            }
            headers.update({
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "upgrade-insecure-requests": "1",
                "referer": f"{const.FRAGMENT_BASE_URL}/",
            })

            async with httpx.AsyncClient(cookies=self._cookies) as session:
                response = await session.get(const.FRAGMENT_BASE_URL, headers=headers)

            if response.status_code != 200:
                raise FragmentSdkExc(message='Error during getting hash')

            match = re.search(r"(?:https://fragment\.com)?/api\?hash=([a-f0-9]+)", response.text)
            if not match:
                raise FragmentSdkExc(message='Error during getting hash')

            self.account_info = {
                'cookies': self._cookies,
                'hash': match.group(1)
            }

            self.http_client = HttpClient(
                cookies=self._cookies,
                _hash=self.account_info['hash']
            )

            await self.ton_wallet_client.async_init()
            self.__async_init = True

    @staticmethod
    def get_cookies() -> dict:
        return get_client_cookies()

    @_require_init
    async def close(self):
        await self.http_client.close()
        await self.ton_wallet_client.close()

    # ------------ MAIN METHODS ------------ #
    @_require_init
    async def buy_stars(
            self,
            username: str,
            quantity: int,
            show_sender: bool = False,
            # payment_method: const.FRAGMENT_PAYMENT_METHOD_TYPE | None = None
    ) -> BuyStarsDto:
        return await buy_stars(
            client=self,
            username=username,
            quantity=quantity,
            show_sender=show_sender,
            # Пока заглушка
            payment_method='ton'
        )

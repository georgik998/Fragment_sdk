from typing import Literal
from functools import wraps
import base64

from tonutils.clients import TonapiClient
from tonutils.types import NetworkGlobalID
from tonutils.contracts.wallet import WalletV4R2, WalletV5R1

from pytoniq_core.boc import Cell

from fragment_sdk.types.exception import TonWalletLowBalanceExc
from fragment_sdk import const


class TonWalletClient:
    _wallet: WalletV4R2 | WalletV5R1
    account_info: dict

    def __init__(self, api_key: str, seed: str, version: Literal['V4R2', 'V5R1'] = 'V5R1'):
        self._api_key: str = api_key
        self._seed: str = seed
        self._version = {
            'V4R2': WalletV4R2,
            'V5R1': WalletV5R1
        }[version]

        self.__async_init = False

    async def async_init(self) -> None:
        if self.__async_init is False:
            async with TonapiClient(network=NetworkGlobalID.MAINNET, api_key=self._api_key) as ton:
                wallet, public_key, private_key, mnemonic_list = self._version.from_mnemonic(
                    client=ton,
                    mnemonic=self._seed
                )

            await wallet.refresh()
            self._wallet = wallet
            self.account_info = {
                "address": self._wallet.address.to_str(False, False),
                "publicKey": public_key.as_hex,
                "chain": const.WALLET_CHAIN,
                "walletStateInit": base64.b64encode(self._wallet.state_init.serialize().to_boc()).decode(),
            }
            self.__async_init = True

    # ---------------- HELP METHODS ---------------- #
    @staticmethod
    def _require_init(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.__init_lock is not None:
                await self.async_init()
            return await func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def __clean_decode(payload: str) -> str | None:
        s = payload.strip()
        if not s:
            return ""
        s += "=" * (-len(s) % 4)
        try:
            boc = base64.b64decode(s)
            cell = Cell.one_from_boc(boc)
            sl = cell.begin_parse()
            sl.load_uint(32)
            return sl.load_snake_string().strip()
        except Exception:
            return None

    # ---------------- LIKE PROPERTY METHODS ---------------- #
    @_require_init
    async def get_balance(self) -> float:
        await self._wallet.refresh()
        return self._wallet.balance / 1_000_000_000

    @_require_init
    async def get_address(self) -> str:
        return self._wallet.address.to_str(False, False)

    # ---------------- MAIN METHODS ---------------- #
    @_require_init
    async def send_transaction(self, fragment_buy_data: dict) -> str | None:
        message = fragment_buy_data["transaction"]["messages"][0]
        amount_ton = int(message["amount"]) / 1_000_000_000
        payload = self.__clean_decode(message["payload"])

        await self._wallet.refresh()

        balance_ton = self._wallet.balance / 1_000_000_000
        required = amount_ton + const.MIN_TON_BALANCE

        if balance_ton <= required:
            raise TonWalletLowBalanceExc(required_balance=required, current_balance=balance_ton)

        result = await self._wallet.transfer(
            destination=message["address"],
            amount=int(message["amount"]),
            body=payload,
        )
        return result.normalized_hash

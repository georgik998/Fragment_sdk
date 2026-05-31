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
    __ton: TonapiClient

    def __init__(self, api_key: str, seed: str, version: const.WALLET_VERSION_TYPE = const.DEFAULT_WALLET_VERSION):
        self._api_key: str = api_key
        self._seed: str = seed
        self._version = const.WALLET_VERSION_DICT[version]

        self.__async_init = False

    async def async_init(self) -> None:
        if self.__async_init is False:
            self.__ton = TonapiClient(
                network=NetworkGlobalID.MAINNET,
                api_key=self._api_key
            )
            await self.__ton.__aenter__()

            wallet, public_key, private_key, mnemonic_list = self._version.from_mnemonic(
                client=self.__ton,
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

    async def close(self):
        if self.__ton:
            await self.__ton.__aexit__(None, None, None)

    # ---------------- HELP METHODS ---------------- #
    @staticmethod
    def _require_init(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.__async_init is False:
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
    async def get_raw_address(self) -> str:
        return self._wallet.address.to_str(False, False)

    @_require_init
    async def get_address(self) -> str:
        return self._wallet.address.to_str()

    # ---------------- MAIN METHODS ---------------- #
    @_require_init
    async def send_transaction(self, fragment_buy_data: dict) -> str | None:
        message = fragment_buy_data["messages"][0]
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

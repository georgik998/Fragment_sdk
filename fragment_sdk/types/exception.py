from typing import Literal


class FragmentSdkExc(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MethodExc(FragmentSdkExc):
    def __init__(
            self,
            method: Literal[
                'buy_stars',
                'buy_premium'
            ],
            stage: Literal['get_recipient', 'get_request_id', 'get_buy_data'],
            detail: Literal['http_request_error', 'parse_error']
    ):
        self.method = method
        self.stage = stage
        self.detail = detail
        message = f"Error during '{method}' at stage '{stage}', detail='{detail}'"
        super().__init__(message)


class VerifyExc(FragmentSdkExc):

    def __init__(self, method: Literal['buy_stars', 'buy_premium']):
        self.method = method
        super().__init__(message=f"Can't complete '{method}', fragment account is unverified")


class TonWalletLowBalanceExc(FragmentSdkExc):

    def __init__(self, required_balance: float, current_balance: float):
        self.current_balance = current_balance
        self.required_balance = required_balance
        message = (
            f"Current wallet balance is too low, "
            f"required balance='{round(required_balance, 1)}', current balance='{round(current_balance, 1)}'"
        )
        super().__init__(message)


class CookieExc(FragmentSdkExc):

    def __init__(self):
        super().__init__('Error during getting cookie, try manual method')

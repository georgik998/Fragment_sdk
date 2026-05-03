from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BuyStarsDto:
    username: str
    quantity: int

    recipient: str
    request_id: str
    buy_data: dict

    tx_hash: str

from typing import TYPE_CHECKING
import json

from fragment_sdk.types.exception import MethodExc, VerifyExc
from fragment_sdk.types.dto import BuyStarsDto
from fragment_sdk._clients.http import HttpExc
from fragment_sdk import const

if TYPE_CHECKING:
    from fragment_sdk._clients.fragment import FragmentClient


async def get_recipient(username: str, quantity: int, client: 'FragmentClient') -> str:
    try:
        response = await client.http_client.post(
            url='/api',
            data={
                "query": username,
                "quantity": quantity,
                "method": "searchStarsRecipient"
            }
        )
        data = response.json()
    except (HttpExc, ValueError):
        raise MethodExc(method='buy_stars', stage='get_recipient', detail='http_request_error')

    recipient = data.get('found', {}).get('recipient')
    if recipient is None:
        raise MethodExc(method='buy_stars', stage='get_recipient', detail='parse_error')
    return recipient


async def get_request_id(
        recipient: str,
        quantity: int,
        payment_method: const.FRAGMENT_PAYMENT_METHOD_TYPE,
        client: 'FragmentClient'
) -> str:
    try:
        response = await client.http_client.post(
            url='/api',
            data={
                "recipient": recipient,
                "quantity": quantity,
                "method": "initBuyStarsRequest",
                "payment_method": payment_method
            }
        )
        data = response.json()
    except (HttpExc, ValueError):
        raise MethodExc(method='buy_stars', stage='get_request_id', detail='http_request_error')

    request_id = data.get("req_id")
    if request_id is None:
        raise MethodExc(method='buy_stars', stage='get_request_id', detail='parse_error')
    return request_id


async def get_buy_data(
        recipient: str,
        req_id: str,
        quantity: int,
        show_sender: bool,
        client: 'FragmentClient'
):
    headers = const.BASE_HEADERS
    headers.update({
        "referer": f"https://fragment.com/stars/buy?recipient={recipient}&quantity={quantity}",
    })
    try:
        response = await client.http_client.post(
            url='/api',
            data={
                "account": json.dumps(client.ton_wallet_client.account_info),
                "device": const.DEVICE_HEADERS,
                "transaction": 1,
                "id": req_id,
                "show_sender": int(show_sender),
                "method": "getBuyStarsLink",
            },
            headers=headers
        )
        data = response.json()
    except (HttpExc, ValueError):
        raise MethodExc(method='buy_stars', stage='get_buy_data', detail='http_request_error')
    if data.get('need_verify') is True:
        raise VerifyExc(method='buy_stars')
    if data.get('transaction', {}).get('messages') is None:
        raise MethodExc(method='buy_stars', stage='get_buy_data', detail='parse_error')
    return data['transaction']


async def buy_stars(
        client: 'FragmentClient',
        username: str,
        quantity: int,
        show_sender: bool,
        payment_method: const.FRAGMENT_PAYMENT_METHOD_TYPE | None
) -> BuyStarsDto:
    recipient = await get_recipient(
        username=username,
        quantity=quantity,
        client=client
    )
    request_id = await get_request_id(
        recipient=recipient,
        quantity=quantity,
        client=client,
        payment_method=payment_method if payment_method is not None else client.payment_method
    )
    buy_data = await get_buy_data(
        show_sender=show_sender,
        recipient=recipient,
        req_id=request_id,
        quantity=quantity,
        client=client
    )
    transaction_hash = await client.ton_wallet_client.send_transaction(fragment_buy_data=buy_data)
    return BuyStarsDto(
        username=username,
        quantity=quantity,
        recipient=recipient,
        request_id=request_id,
        buy_data=buy_data,
        tx_hash=transaction_hash
    )

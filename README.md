# SDK для работы с фрагментом

### fragment_sdk v0.1.0

### Code by George

----

## ❓ В чем суть проекта

Данная библиотека позволяет удобно работать с площадкой телеграм [fragment](https://fragment.com/)

Не нужно с нуля писать парсер, можно использовать данное готовое решение, удобно совершая

покупки на fragment, используя необходимые методы класса `FragmentClient`

## Какие действия с платформой системы сейчас поддерживаются ?

- Покупка звезд
- **Поддержка различных сетей для оплаты покупок на fragment находится в разработке**

## ⚙️ Стек

- `httpx` - для работы с http запросами
- `tonutils` - для работы с ton кошельком

## 📁 Структура

```text
├── /fragment_sdk
│   ├── __init__.py     # Основные импорты
│   ├── /clients 
│   │   ├── fragment.py # клиент для работы с фрагментом
│   │   ├── http.py # клиент для работы с http запросами
│   │   └── wallet.py  # клиент для работы с ton кошельком
│   ├── /types
│   │   ├── dto.py  # типы для возвращаемых значений функций у FragmentClient
│   │   └── exception.py
│   ├── /methods    # Логика работы с фрагментом
│   │   ├── cookie.py
│   │   └── buy_stars.py
├── README.md
└── requirements.txt
```

## Важные замечания

Все ошибки которые может выкинуть библиотека, наследуются от одного общего исключения:

```python
from fragment_sdk.types.exception import FragmentSdkExc
```

Любую ошибку можно отловить, используя `FragmentSdkExc`

## Как получить необходимые для запуска данные ?

Для работы с библиотекой требуются следующие данные:

| Параметр         | Description                                        |
|------------------|----------------------------------------------------|
| `seed`           | сид фраза кошелька из 24 слов                      |
| `api_key`        | апи ключ  [tonconsole.com](https://tonconsole.com) |
| `stel_ssid`      | fragment cookie с названием: `stel_ssid`           |
| `stel_token`     | fragment cookie с названием: `stel_token`          |
| `stel_dt`        | fragment cookie с названием: `stel_dt`             |
| `stel_ton_token` | fragment cookie с названием: `stel_ton_token`      |

**1. Fragment cookies**

Для начала зарегистрируйтесь на [fragment.com](https://fragment.com) и подключите свой TON кошелек

Теперь можно получить куки двумя способами:

- **Автоматические** (рекомендуется) — вызовите метод `get_cookies()` у класса `FragmentClient`

  У вас откроется окно браузера, где нужно будет войти в свой аккаунт фрагмента и подключить кошелек
  (**важно, используйте аккаунт и кошелек с которых планируете совершать покупки в дальнейшем**),
  после чего нажать Enter в консоли откуда

  запускали скрипт по получению кук
  ```python
  from fragment_sdk import FragmentClient
  from fragment_sdk.types.exception import CookieExc
  
  try:
    cookies = FragmentClient.get_cookies()
    print("Ваши куки для вставки:\n", "\n".join(f"{key}={value}" for key, value in cookies.items()))
  except CookieExc:
    print('Ошибка во время получения кук, попробуйте ручной способ')
  ```

- **Ручной** — установите
  расширение [Cookie Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) и
  возьмите куки со следующими названиями:

  `stel_ssid`, `stel_dt`, `stel_token`, `stel_ton_token`

**2. Tonapi key** — получите на  [tonconsole.com](https://tonconsole.com).

**3. Seed phrase** - сид фраза кошелька состоящая из 24 слов

## Быстрый старт на примере покупки звезд

```python
from fragment_sdk import FragmentClient
from fragment_sdk.types.exception import FragmentSdkExc, FragmentMethodExc, TonWalletLowBalanceExc

STEL_SSID = input('Введите stel_ssid из cookie фрагмента:\n')
STEL_TOKEN = input('Введите stel_token из cookie фрагмента:\n')
STEL_DT = input('Введите stel_dt из cookie фрагмента:\n')
STEL_TON_TOKEN = input('Введите stel_ton_token из cookie фрагмента:\n')
SEED = input('Введите seed фразу кошелька:\n')
API_KEY = input('Введите api ключ ton:\n')
TG_USERNAME = input('Введите юзернейм на чье имя хотите купить звезды (должно начинаться с @): ')
STARS_QUANTITY = int(input('Введите желаемое количество звезд для покупки (минимум 50): '))


async def main():
    client = FragmentClient(
        stel_ssid=STEL_SSID,
        stel_token=STEL_TOKEN,
        stel_dt=STEL_DT,
        stel_ton_token=STEL_TON_TOKEN,
        seed=SEED,
        api_key=API_KEY
    )

    # Вызов 'async_init' опционален - он будет автоматически вызван при использовании любого метода класса,
    # но лучше вызвать его в ручную для обработки возможной ошибки
    try:
        await client.async_init()
    except FragmentSdkExc as e:
        print(e, e.message)

    try:
        from fragment_sdk.types.dto import BuyStarsDto

        result: BuyStarsDto = await client.buy_stars(
            username=TG_USERNAME,
            quantity=STARS_QUANTITY,
            show_sender=False
        )
        print(result)
    except FragmentMethodExc as e:
        print(e, e.message, e.stage, e.method, e.detail)
    except TonWalletLowBalanceExc as e:
        print(e, e.current_balance, e.required_balance)

        # Закрываем httpx.AsyncClient и TonApiClient сессии
        await client.close()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
```
import httpx

from fragment_sdk.const import FRAGMENT_BASE_URL


class HttpExc(Exception):

    def __init__(
            self,
            error_type: str = "",
            error_message: str = "",
            status_code: int | None = None,
            response_headers: dict | None = None,
            response_body: str | None = None
    ):
        self.error_type = error_type
        self.error_message = error_message
        self.status_code = status_code
        self.response_headers = response_headers
        self.response_body = response_body
        super().__init__(self.error_message)

    def __str__(self) -> str:
        parts = []
        if self.error_type:
            parts.append(f"[{self.error_type}]")
        if self.status_code:
            parts.append(f"HTTP {self.status_code}")
        if self.error_message:
            parts.append(self.error_message)
        return " ".join(parts) if parts else super().__str__()


class HttpClient:

    def __init__(self, cookies: dict, _hash: str, url: str = FRAGMENT_BASE_URL):
        self.httpx_client = httpx.AsyncClient(
            cookies=cookies,
            base_url=url,
            params={
                'hash': _hash
            }
        )

    async def close(self):
        await self.httpx_client.aclose()

    async def request(self, method: str, url: str = "", **kwargs) -> httpx.Response:
        try:
            response = await self.httpx_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as e:
            raise HttpExc(
                error_type="timeout_error",
                error_message=f"Request timeout after {self.httpx_client.timeout.connect}s",
                status_code=None,
                response_headers=None,
                response_body=None
            ) from e
        except httpx.TooManyRedirects as e:
            raise HttpExc(
                error_type="redirect_error",
                error_message=f"Too many redirects: {str(e)}",
                status_code=None,
                response_headers=None,
                response_body=None
            ) from e

        except httpx.HTTPStatusError as e:
            if "application/json" in e.response.headers.get("content-type", ""):
                data = e.response.json()
            else:
                data = None
            raise HttpExc(
                error_type=f"http_{e.response.status_code}_error",
                error_message=str(e),
                status_code=e.response.status_code,
                response_headers=dict(e.response.headers),
                response_body=data
            ) from e

        except httpx.RequestError as e:
            raise HttpExc(
                error_type="request_error",
                error_message=f"Request failed: {str(e)}",
                status_code=None,
                response_headers=None,
                response_body=None
            ) from e
        except Exception as e:
            raise HttpExc(
                error_type="unexpected_error",
                error_message=f"Unexpected error: {str(e)}",
                status_code=None,
                response_headers=None,
                response_body=None
            ) from e

    async def get(self, url: str = "", **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str = "", **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

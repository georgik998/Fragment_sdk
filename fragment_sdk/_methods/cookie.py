import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

from fragment_sdk.const import FRAGMENT_BASE_URL
from fragment_sdk.types.exception import CookieExc

BASE_DIR = Path("fragment_sdk_get_cookie_temp")
VENV_DIR = BASE_DIR / "venv"
BROWSERS_DIR = BASE_DIR / "browsers"
CACHE_DIR = BASE_DIR / "cache"

GET_COOKIES_CODE: str = r"""
import json
import sys
from urllib.parse import urlparse
from pathlib import Path

from playwright.sync_api import sync_playwright

url = sys.argv[1]
output_file = sys.argv[2]

domain = urlparse(url).hostname

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    page.goto(url)

    input("\t(2.1) После логина, нажмите ENTER...")

    cookies = context.cookies()
    browser.close()

    result = {
        c["name"]: c["value"]
        for c in cookies
        if domain in c["domain"]
    }

    Path(output_file).write_text(json.dumps(result))
"""


def _install_playwright():
    print("(1) Устанавливаем необходимые библиотеки, пожалуйста подождите...")

    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR, ignore_errors=True)
    BASE_DIR.mkdir(exist_ok=True)

    subprocess.check_call([
        sys.executable, "-m", "venv", str(VENV_DIR)
    ])

    if os.name == "nt":
        python_bin = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_bin = VENV_DIR / "bin" / "python"

    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSERS_DIR)
    env["XDG_CACHE_HOME"] = str(CACHE_DIR)

    subprocess.check_call([
        str(python_bin), "-m", "pip", "install", "--upgrade", "pip", "-q"
    ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call([
        str(python_bin), "-m", "pip", "install", "playwright", "-q"
    ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call([
        str(python_bin), "-m", "playwright", "install", "chromium"
    ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    (BASE_DIR / "worker.py").write_text(GET_COOKIES_CODE, encoding="utf-8")

    print("\t(1.1) Все библиотеки успешно скачаны!")


def _parse_cookies() -> dict:
    print("(2) Войдите на сайт, чтобы получить cookie")

    if os.name == "nt":
        python_bin = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_bin = VENV_DIR / "bin" / "python"

    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSERS_DIR)
    env["XDG_CACHE_HOME"] = str(CACHE_DIR)

    result_file = BASE_DIR / "cookies.json"

    subprocess.run(
        [
            str(python_bin),
            str(BASE_DIR / "worker.py"),
            FRAGMENT_BASE_URL,
            str(result_file)
        ],
        env=env,
        check=True
    )

    if not result_file.exists():
        raise CookieExc()

    return json.loads(result_file.read_text())


def _uninstall_playwright():
    print("(3) Удаляем все скачанные библиотеки...")
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR, ignore_errors=True)
    print("\t(3.1) Все скачанные библиотеки успешно удалены!")


def get_cookies() -> dict:
    try:
        _install_playwright()
        cookies = _parse_cookies()
        try:
            return {
                'stel_ssid': cookies['stel_ssid'],
                'stel_token': cookies['stel_token'],
                'stel_dt': cookies['stel_dt'],
                'stel_ton_token': cookies['stel_ton_token']
            }
        except KeyError:
            raise CookieExc()
    finally:
        _uninstall_playwright()




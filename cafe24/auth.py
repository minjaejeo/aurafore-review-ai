import os
import json
import base64
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

MALL_ID = os.getenv("CAFE24_MALL_ID")
CLIENT_ID = os.getenv("CAFE24_CLIENT_ID")
CLIENT_SECRET = os.getenv("CAFE24_CLIENT_SECRET")
BASE_URL = f"https://{MALL_ID}.cafe24api.com/api/v2"
TOKEN_FILE = ".cafe24_token.json"


def _credentials_header() -> str:
    return base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()


def save_token(token_data: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)


def load_token() -> dict | None:
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


def is_token_expired(token_data: dict) -> bool:
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    return datetime.now() >= expires_at - timedelta(minutes=5)


def refresh_access_token(refresh_token: str) -> dict:
    response = httpx.post(
        f"{BASE_URL}/oauth/token",
        headers={
            "Authorization": f"Basic {_credentials_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    response.raise_for_status()
    data = response.json()
    data["expires_at"] = (
        datetime.now() + timedelta(seconds=data["expires_in"])
    ).isoformat()
    save_token(data)
    return data


def get_access_token() -> str:
    token_data = load_token()
    if token_data is None:
        raise RuntimeError(
            "토큰이 없습니다. 서버를 실행하고 http://localhost:8000/cafe24/auth 를 방문해서 로그인해주세요."
        )
    if is_token_expired(token_data):
        token_data = refresh_access_token(token_data["refresh_token"])
    return token_data["access_token"]


def get_auth_url() -> str:
    redirect_uri = os.getenv("CAFE24_REDIRECT_URI")
    return (
        f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=mall.read_community"
    )


def exchange_code_for_token(code: str) -> dict:
    redirect_uri = os.getenv("CAFE24_REDIRECT_URI")
    response = httpx.post(
        f"{BASE_URL}/oauth/token",
        headers={
            "Authorization": f"Basic {_credentials_header()}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
    )
    response.raise_for_status()
    data = response.json()
    data["expires_at"] = (
        datetime.now() + timedelta(seconds=data["expires_in"])
    ).isoformat()
    save_token(data)
    return data

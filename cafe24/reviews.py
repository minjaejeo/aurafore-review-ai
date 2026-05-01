import httpx
from cafe24.auth import get_access_token, BASE_URL

HEADERS_EXTRA = {"X-Cafe24-Api-Version": "2024-06-01"}


def _auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
        **HEADERS_EXTRA,
    }


def fetch_reviews(product_no: int = None, limit: int = 100, offset: int = 0) -> list[dict]:
    params = {"shop_no": 1, "limit": limit, "offset": offset}
    if product_no:
        params["product_no"] = product_no

    response = httpx.get(
        f"{BASE_URL}/admin/reviews",
        headers=_auth_headers(),
        params=params,
    )
    response.raise_for_status()
    return response.json().get("reviews", [])


def fetch_all_reviews(product_no: int = None) -> list[dict]:
    all_reviews = []
    offset = 0
    limit = 100

    while True:
        batch = fetch_reviews(product_no=product_no, limit=limit, offset=offset)
        if not batch:
            break
        all_reviews.extend(batch)
        print(f"  가져온 리뷰: {len(all_reviews)}개...")
        if len(batch) < limit:
            break
        offset += limit

    print(f"총 {len(all_reviews)}개 리뷰 수집 완료")
    return all_reviews

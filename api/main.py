import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from db.database import init_db, get_reviews_by_skin_type, get_all_reviews
from cafe24.auth import get_auth_url, exchange_code_for_token

load_dotenv()
init_db()

app = FastAPI(title="Aurafore Review AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "Aurafore Review AI"}


@app.get("/cafe24/auth", response_class=HTMLResponse)
def cafe24_auth():
    url = get_auth_url()
    return f"""
    <html><body>
    <h2>카페24 로그인</h2>
    <a href="{url}" style="font-size:18px;padding:12px 24px;background:#333;color:#fff;text-decoration:none;border-radius:6px;">
      카페24 계정으로 로그인
    </a>
    </body></html>
    """


@app.get("/cafe24/callback")
def cafe24_callback(code: str):
    exchange_code_for_token(code)
    return {"message": "인증 완료! 이제 리뷰를 수집할 수 있습니다."}


@app.get("/reviews")
def get_reviews(
    skin_type: str = Query(None, description="피부 타입 필터 (민감성, 건성, 지성, 복합성, 아토피)"),
    product_no: str = Query(None, description="상품 번호"),
):
    if skin_type:
        reviews = get_reviews_by_skin_type(skin_type, product_no)
    else:
        reviews = get_all_reviews(product_no)
    return {"total": len(reviews), "skin_type_filter": skin_type, "reviews": reviews}


@app.get("/reviews/summary")
def get_summary(product_no: str = Query(None)):
    reviews = get_all_reviews(product_no)
    skin_type_counts: dict = {}
    for review in reviews:
        for st in review["skin_types"]:
            skin_type_counts[st] = skin_type_counts.get(st, 0) + 1
    return {"total_reviews": len(reviews), "skin_type_distribution": skin_type_counts}

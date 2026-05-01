"""
전체 파이프라인 실행 스크립트.
1단계: 카페24에서 리뷰 수집
2단계: Claude AI로 분석
3단계: DB에 저장

실행 방법: python run_pipeline.py
특정 상품만: python run_pipeline.py --product-no 12345
"""
import argparse
from cafe24.reviews import fetch_all_reviews
from ai.analyzer import analyze_reviews_batch
from db.database import init_db, save_many_reviews

def main(product_no: int = None):
    init_db()

    print("=" * 50)
    print("1단계: 카페24 리뷰 수집 중...")
    reviews = fetch_all_reviews(product_no=product_no)

    if not reviews:
        print("수집된 리뷰가 없습니다.")
        return

    print(f"\n2단계: Claude AI로 {len(reviews)}개 리뷰 분석 중...")
    analyzed = analyze_reviews_batch(reviews)

    print(f"\n3단계: DB에 {len(analyzed)}개 저장 중...")
    save_many_reviews(analyzed)

    print("\n완료!")
    print("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-no", type=int, help="특정 상품 번호")
    args = parser.parse_args()
    main(product_no=args.product_no)

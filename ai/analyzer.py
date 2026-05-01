import json
import anthropic

client = anthropic.Anthropic()

# 시스템 프롬프트는 모든 요청에서 동일하므로 캐시 적용
SYSTEM_PROMPT = """당신은 화장품 리뷰 분석 전문가입니다.
주어진 리뷰에서 고객의 피부 정보와 만족도를 추출하여 JSON만 반환하세요.

반환 형식:
{
  "skin_types": ["민감성|건성|지성|복합성|아토피|중성 중 해당 항목"],
  "skin_concerns": ["등드름|여드름|모공|색소침착|건조함|가려움|트러블|자극 중 해당 항목"],
  "satisfaction": 1~5 숫자 (1:매우불만, 5:매우만족),
  "keywords": ["핵심 키워드 3~5개"]
}

규칙:
- JSON 외 텍스트 절대 금지
- 피부 정보 미언급 시 빈 배열([])
- 만족도 불명확 시 3 반환"""


def analyze_review(review_text: str) -> dict:
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{
                "role": "user",
                "content": review_text,
            }],
        )
        return json.loads(response.content[0].text.strip())

    except (json.JSONDecodeError, Exception):
        return {
            "skin_types": [],
            "skin_concerns": [],
            "satisfaction": 3,
            "keywords": [],
        }


def analyze_reviews_batch(reviews: list[dict]) -> list[dict]:
    results = []
    for i, review in enumerate(reviews, 1):
        text = review.get("content") or review.get("review_body", "")
        if not text.strip():
            continue

        print(f"  분석 중 ({i}/{len(reviews)}): {text[:30]}...")
        analysis = analyze_review(text)
        results.append({
            "review_no": review.get("review_no"),
            "product_no": review.get("product_no"),
            "member_id": review.get("member_id", ""),
            "review_text": text,
            "rating": review.get("rating", 0),
            **analysis,
        })

    return results

import anthropic
import requests
import os
import json
from datetime import datetime
from base64 import b64encode

# 設定
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WP_URL = os.environ.get("WP_URL", "https://goen-business.com")
WP_USER = os.environ.get("WP_USER", "AdminGOEN")
WP_APP_PASSWORD = os.environ["WP_APP_PASSWORD"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# 曜日別テーマ
THEMES = {
    0: {"ja": "日本人上司が「報連相」にこだわる理由", "vi": "Tại sao sếp Nhật luôn yêu cầu báo cáo thường xuyên?"},
    1: {"ja": "ベトナム人部下のやる気を引き出す問いかけ方", "vi": "Cách đặt câu hỏi để khơi dậy động lực nhân viên"},
    2: {"ja": "製造業で実際にあった研修導入の事例", "vi": "Case study thực tế: Đào tạo tại nhà máy sản xuất"},
    3: {"ja": "評価面談で使える5つのフレーズ", "vi": "5 câu nói hiệu quả trong buổi đánh giá nhân viên"},
    4: {"ja": "「沈黙」の意味が日越で全然違う話", "vi": "Sự im lặng mang ý nghĩa khác nhau ở Nhật và Việt Nam"},
    5: {"ja": "日越インターン受け入れの心得", "vi": "Chuẩn bị gì trước khi tiếp nhận thực tập sinh Nhật Bản?"},
    6: {"ja": "ベトナム現地化を進める上で大切な考え方", "vi": "Tư duy quan trọng khi thúc đẩy địa phương hóa tại Việt Nam"},
}

KNOWLEDGE = """
会社名: GOEN Business Training（代表：川村泰裕、ホーチミン市）
事業: ベトナム進出日系企業向け企業研修・人材育成、日越インターンシップ
ミッション: 「ベトナムの現場に、育つ文化をつくる」
ターゲット（日本語）: 製造業・労働集約型の日系企業社長・管理部部長
ターゲット（ベトナム語）: 日系企業のHRマネージャー・総務マネージャー（女性・40代前後）
トーン（日本語）: 現場感があり共感ベース。具体的な場面描写を入れる。上から目線禁止。
トーン（ベトナム語）: 親しみやすく実用的。先輩が後輩に教える感覚。
CTA（日本語）: GOENでは、ベトナム進出日系企業の人材育成を専門にサポートしています。まずは無料相談からどうぞ。▶ https://goen-business.com/lien-he/
CTA（ベトナム語）: GOEN cung cấp chương trình đào tạo cho doanh nghiệp Nhật Bản tại Việt Nam. Liên hệ tư vấn miễn phí: https://goen-business.com/lien-he/
"""

def generate_article(theme, lang):
    if lang == "ja":
        prompt = f"""あなたはGOEN Business Trainingの専属ライターです。
ナレッジ: {KNOWLEDGE}
テーマ: {theme}
以下の形式で記事を書いてください。

---TITLE---
（タイトル）
---BODY---
（本文・マークダウン・800〜1200字）
---CTA---
（問い合わせ誘導文）
---TAGS---
（タグ3〜5個、カンマ区切り）"""
    else:
        prompt = f"""Bạn là copywriter của GOEN Business Training.
Knowledge: {KNOWLEDGE}
Chủ đề: {theme}
Hãy viết bài theo định dạng sau:

---TITLE---
（tiêu đề）
---BODY---
（nội dung markdown・800〜1200 từ）
---CTA---
（CTA）
---TAGS---
（3〜5 tags, ngăn cách bằng dấu phẩy）"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def parse_article(raw):
    result = {"title": "", "body": "", "cta": "", "tags": []}
    if "---TITLE---" in raw:
        result["title"] = raw.split("---TITLE---")[1].split("---BODY---")[0].strip()
    if "---BODY---" in raw:
        result["body"] = raw.split("---BODY---")[1].split("---CTA---")[0].strip()
    if "---CTA---" in raw:
        result["cta"] = raw.split("---CTA---")[1].split("---TAGS---")[0].strip()
    if "---TAGS---" in raw:
        result["tags"] = [t.strip() for t in raw.split("---TAGS---")[1].strip().split(",")]
    return result

def post_to_wordpress(article, lang="ja"):
    credentials = b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }

    content = f"{article['body']}\n\n---\n{article['cta']}"

    if lang == "ja":
        categories_name = "人材育成"
    else:
        categories_name = "Đào tạo nhân sự"

    data = {
        "title": article["title"],
        "content": content,
        "status": "draft",  # 下書きとして保存（確認後に公開）
        "excerpt": article["body"][:100],
    }

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        headers=headers,
        json=data
    )

    if response.status_code in [200, 201]:
        post_id = response.json().get("id")
        print(f"✅ 投稿成功 (lang={lang}): ID={post_id}, タイトル={article['title']}")
        return True
    else:
        print(f"❌ 投稿失敗 (lang={lang}): {response.status_code} - {response.text}")
        return False

# メイン処理
today = datetime.now()
weekday = today.weekday()
theme = THEMES[weekday]
date_str = today.strftime("%Y-%m-%d")

print(f"📝 {date_str} の記事を生成・投稿します")
print(f"テーマ（日本語）: {theme['ja']}")
print(f"Chủ đề (tiếng Việt): {theme['vi']}")

# 日本語記事
print("\n--- 日本語記事を生成中 ---")
ja_raw = generate_article(theme["ja"], "ja")
ja_article = parse_article(ja_raw)
post_to_wordpress(ja_article, "ja")

# ベトナム語記事
print("\n--- ベトナム語記事を生成中 ---")
vi_raw = generate_article(theme["vi"], "vi")
vi_article = parse_article(vi_raw)
post_to_wordpress(vi_article, "vi")

print("\n🎉 本日の記事生成・投稿完了!")

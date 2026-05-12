import anthropic
import os
import json
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

with open("goen_knowledge.md", "r", encoding="utf-8") as f:
    knowledge = f.read()

THEMES = {
    0: {"ja": "日本人上司が「報連相」にこだわる理由", "vi": "Tại sao sếp Nhật luôn yêu cầu báo cáo thường xuyên?"},
    1: {"ja": "ベトナム人部下のやる気を引き出す問いかけ方", "vi": "Cách đặt câu hỏi để khơi dậy động lực nhân viên"},
    2: {"ja": "製造業で実際にあった研修導入の事例", "vi": "Case study thực tế: Đào tạo tại nhà máy sản xuất"},
    3: {"ja": "評価面談で使える5つのフレーズ", "vi": "5 câu nói hiệu quả trong buổi đánh giá nhân viên"},
    4: {"ja": "「沈黙」の意味が日越で全然違う話", "vi": "Sự im lặng mang ý nghĩa khác nhau ở Nhật và Việt Nam"},
    5: {"ja": "日越インターン受け入れの心得", "vi": "Chuẩn bị gì trước khi tiếp nhận thực tập sinh Nhật Bản?"},
    6: {"ja": "ベトナム現地化を進める上で大切な考え方", "vi": "Tư duy quan trọng khi thúc đẩy địa phương hóa tại Việt Nam"},
}

today = datetime.now()
weekday = today.weekday()
theme = THEMES[weekday]
date_str = today.strftime("%Y-%m-%d")

def generate_article(theme_title, lang="ja"):
    if lang == "ja":
        prompt = f"""あなたはGOEN Business Trainingの専属ライターです。
以下のナレッジベースを参照して、日本語のWordPressコラム記事を1本書いてください。

【ナレッジベース】
{knowledge[:3000]}

【今日のテーマ】
{theme_title}

【出力形式】
---TITLE---
（タイトル）
---BODY---
（本文・マークダウン形式・800〜1200字）
---CTA---
（問い合わせ誘導文）
---TAGS---
（タグ3〜5個、カンマ区切り）
"""
    else:
        prompt = f"""Bạn là copywriter chuyên nghiệp của GOEN Business Training.
Dựa trên knowledge base dưới đây, hãy viết 1 bài blog tiếng Việt cho WordPress.

【Knowledge Base】
{knowledge[:3000]}

【Chủ đề hôm nay】
{theme_title}

【Định dạng đầu ra】
---TITLE---
（tiêu đề）
---BODY---
（nội dung markdown・800〜1200 từ）
---CTA---
（CTA tiếng Việt）
---TAGS---
（3〜5 tags, ngăn cách bằng dấu phẩy）
"""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def parse_article(raw_text):
    result = {"title": "", "body": "", "cta": "", "tags": []}
    if "---TITLE---" in raw_text:
        result["title"] = raw_text.split("---TITLE---")[1].split("---BODY---")[0].strip()
    if "---BODY---" in raw_text:
        result["body"] = raw_text.split("---BODY---")[1].split("---CTA---")[0].strip()
    if "---CTA---" in raw_text:
        result["cta"] = raw_text.split("---CTA---")[1].split("---TAGS---")[0].strip()
    if "---TAGS---" in raw_text:
        tags_str = raw_text.split("---TAGS---")[1].strip()
        result["tags"] = [t.strip() for t in tags_str.split(",")]
    return result

print(f"📝 {date_str} の記事を生成中...")
print(f"テーマ（日本語）: {theme['ja']}")
print(f"Chủ đề (tiếng Việt): {theme['vi']}")

ja_article = parse_article(generate_article(theme["ja"], "ja"))
vi_article = parse_article(generate_article(theme["vi"], "vi"))

output = {
    "date": date_str,
    "japanese": ja_article,
    "vietnamese": vi_article
}

os.makedirs("articles", exist_ok=True)
output_file = f"articles/{date_str}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ 記事生成完了: {output_file}")
print(f"日本語タイトル: {ja_article['title']}")
print(f"Tiêu đề tiếng Việt: {vi_article['title']}")

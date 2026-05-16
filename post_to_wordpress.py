import anthropic
import requests
import os
import random
import json
import base64
from datetime import datetime

# =============================
# 環境変数
# =============================
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLOUDFLARE_WORKER_URL = os.environ["CLOUDFLARE_WORKER_URL"]
CF_SECRET_KEY = os.environ["CF_SECRET_KEY"]
WP_URL = os.environ.get("WP_URL", "https://goen-business.com")
WP_USER = os.environ.get("WP_USER", "kawamurayasuhiro")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# =============================
# GOENの知識・思想ベース
# =============================
KNOWLEDGE = """
【会社情報】
会社名: GOEN Business Training（代表：川村泰裕、ホーチミン市）
事業: ベトナム進出日系企業向け企業研修・人材育成、日越インターンシップ
ミッション: 「ベトナムの現場に、育つ文化をつくる」
ウェブサイト: https://goen-business.com

【GOENの核心思想・キーワード】
- Mind-Up（マインドアップ）: 目線を上げ続ける。現状に満足せず、常に一段上の視点を持つ組織文化
- 量（りょう）と筋（すじ）: ベトナム人スタッフの2タイプ。「量」=指示通り動ける実行力型、「筋」=本質を掴む思考型
- 現地化（ローカライゼーション）: 日本のやり方を押しつけることではなく、現地スタッフが自分のメリットを実感できる動機設計
- 自律型人材: 「指示待ち」から「自ら考えて動く」への転換。GOENが目指す人材像
- 組織文化の醸成: 研修1回で終わらせない。日常の仕組みとして文化に変えていく
- QC・トヨタ式8ステップ: ベトナム現場での問題解決フレームワーク。現地スタッフへの定着術

【SEOキーワード（必ず含める）】
メインキーワード: マネジメント、研修、ベトナム人、管理職、教育
サブキーワード: 現地化、人材育成、日系企業、ホーチミン、組織文化

【ターゲット読者】
日本語: 在越日系企業の社長・管理部長（製造業・労働集約型）。現場で実際に悩んでいる人。「わかる、うちも同じ」と感じてもらうことが最優先。
ベトナム語: 日系企業のHRマネージャー（40代女性が多い）。実務経験豊富で現場をよく知っている。先輩から学ぶ感覚で読んでもらう。

【トーン】
日本語: 現場感があり共感ベース。具体的な場面描写を入れる。上から目線禁止。「〜ですよね」「〜ではないでしょうか」など問いかけを使う。
ベトナム語: 親しみやすく実用的。丁寧だが堅くない。先輩が後輩に教える感覚。

【CTA】
日本語: GOENでは、在越日系企業の人材育成・現地化推進を専門にサポートしています。まずは無料相談からどうぞ。▶ https://goen-business.com/lien-he/
ベトナム語: GOEN cung cấp chương trình đào tạo chuyên biệt cho doanh nghiệp Nhật Bản tại Việt Nam. Liên hệ tư vấn miễn phí: https://goen-business.com/lien-he/
"""

# =============================
# コンテンツカレンダー（3種類ローテーション）
# 種類A: 思想・解説コラム
# 種類B: 実践・HOWTOコラム
# 種類C: 匿名事例コラム
# =============================
CONTENT_CALENDAR = [
    # Week 1
    {"type": "A", "ja": "「現地化」とは何か。日本のやり方を押しつけることではない",
     "vi": "Bản địa hóa thực sự là gì? Không phải áp đặt văn hóa Nhật"},
    {"type": "B", "ja": "「指示待ち人材」を変える3つの問いかけ。管理職が今日から使えるフレーズ",
     "vi": "3 câu hỏi giúp nhân viên thoát khỏi tư duy 'chờ lệnh'"},
    {"type": "C", "ja": "【事例】製造業A社が現地マネージャー育成に成功した理由",
     "vi": "【Case study】Tại sao công ty sản xuất A thành công trong việc phát triển quản lý người Việt?"},

    # Week 2
    {"type": "A", "ja": "Mind-Upとは何か。目線を上げ続ける組織のつくり方",
     "vi": "Mind-Up là gì? Cách xây dựng tổ chức không ngừng nâng tầm tư duy"},
    {"type": "B", "ja": "「報連相」が上がってこない本当の理由と、今すぐできる対策",
     "vi": "Vì sao nhân viên không báo cáo? Giải pháp thực tế từ ngày hôm nay"},
    {"type": "C", "ja": "【事例】駐在員ゼロでも回る組織をつくったB社の3年間",
     "vi": "【Case study】3 năm xây dựng tổ chức vận hành tốt không cần người Nhật của công ty B"},

    # Week 3
    {"type": "A", "ja": "「量（りょう）」と「筋（すじ）」——ベトナム人スタッフの2つのタイプを知る",
     "vi": "Tư duy 'Ryo' và 'Suji' – Hiểu để phát triển nhân viên đúng hướng"},
    {"type": "B", "ja": "現地マネージャーへの権限委譲。失敗しない5つのステップ",
     "vi": "5 bước giao quyền cho quản lý người Việt mà không sợ thất bại"},
    {"type": "C", "ja": "【事例】研修1回で終わらせなかったC社。文化として定着するまでの道のり",
     "vi": "【Case study】Công ty C đã biến đào tạo thành văn hóa tổ chức như thế nào?"},

    # Week 4
    {"type": "A", "ja": "「個人の集合体」から「組織として動くチーム」へ。現地化の本質",
     "vi": "Từ tập hợp cá nhân đến đội nhóm hành động vì tổ chức"},
    {"type": "B", "ja": "QCとトヨタ式8ステップがベトナム現場で効く理由と導入のコツ",
     "vi": "Tại sao QC và 8 bước Toyota hiệu quả tại Việt Nam? Bí quyết triển khai"},
    {"type": "C", "ja": "【事例】日越コミュニケーションの断絶を乗り越えたD社の取り組み",
     "vi": "【Case study】Công ty D đã vượt qua rào cản giao tiếp Nhật-Việt như thế nào?"},
]

# =============================
# ホーチミン写真リスト（GOENオリジナル）
# =============================
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/GOENBusinessTraining/goen-marketing-auto/main/"

HCMC_PHOTOS = [
    GITHUB_RAW_BASE + "20240323_083025.jpg",
    GITHUB_RAW_BASE + "20241001_145657.jpg",
    GITHUB_RAW_BASE + "IMG_2589.jpg",
    GITHUB_RAW_BASE + "IMG_2682.jpg",
    GITHUB_RAW_BASE + "IMG_3133.jpg",
    GITHUB_RAW_BASE + "IMG_3459.jpg",
    GITHUB_RAW_BASE + "IMG_3467.jpg",
    GITHUB_RAW_BASE + "IMG_3477.jpg",
    GITHUB_RAW_BASE + "IMG_3505.jpg",
    GITHUB_RAW_BASE + "IMG_3511.jpg",
    GITHUB_RAW_BASE + "IMG_3512.jpg",
]

# =============================
# 記事生成（SEO・AEO対応）
# =============================
def generate_article(theme, lang, content_type):
    type_instruction = {
        "A": {
            "ja": "思想・解説コラム。GOENの核心思想（Mind-Up・現地化・量と筋）を軸に、在越日系企業の経営者が「なるほど」と膝を打つ深い洞察を書く。",
            "vi": "Bài viết tư tưởng. Giải thích sâu về triết lý GOENcho HR Manager người Việt."
        },
        "B": {
            "ja": "実践・HOWTOコラム。明日から現場で使える具体的な手法・フレーズ・ステップを書く。箇条書きや番号リストを活用。",
            "vi": "Bài hướng dẫn thực hành. Cung cấp các bước cụ thể, câu mẫu có thể dùng ngay tại công ty."
        },
        "C": {
            "ja": "匿名事例コラム。「ある〇〇業の日系企業A社」という形で、GOENが実際に支援した企業の変化を匿名で描く。Before/Afterを明確に。社名は絶対に出さない。",
            "vi": "Bài case study ẩn danh. Mô tả sự thay đổi thực tế của doanh nghiệp (gọi là 'Công ty A') mà GOEN đã hỗ trợ. Không nêu tên công ty thật."
        },
    }

    if lang == "ja":
        prompt = f"""あなたはGOEN Business Trainingの専属コンテンツライターです。

【GOENナレッジ】
{KNOWLEDGE}

【記事種別】
{type_instruction[content_type]['ja']}

【テーマ】
{theme}

以下の形式で記事を作成してください。SEOとAI検索（AEO）に最適化すること。

---TITLE---
（SEO最適化タイトル。32文字以内。メインキーワードを含める）

---SEO_TITLE---
（検索エンジン用タイトル。32文字以内）

---META_DESC---
（メタディスクリプション。120文字以内。キーワードとCTAを含める）

---FOCUS_KEYWORD---
（Rank Math用フォーカスキーワード。1〜2語）

---BODY---
（本文。以下の構成で書くこと）
## （リード文：読者の悩みに共感する問いかけから始める）

## （H2見出し1：問題の本質）
（本文300字程度）

## （H2見出し2：GOENの視点・解決策）
（本文300字程度。Mind-Up・現地化・量と筋などGOENキーワードを自然に使う）

## （H2見出し3：具体的なアクション・まとめ）
（本文300字程度）

## よくある質問
### Q1. （読者がよく持つ疑問）
A1. （簡潔な回答。AI検索に引っかかるよう具体的に）

### Q2. （別の疑問）
A2. （簡潔な回答）

---CTA---
（問い合わせ誘導文。GOENのCTAを使う）

---SCHEMA---
（Article構造化データのJSON-LD。以下のフォーマットで）
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "（タイトル）",
  "description": "（メタディスクリプション）",
  "author": {{
    "@type": "Organization",
    "name": "GOEN Business Training"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "GOEN Business Training",
    "url": "https://goen-business.com"
  }},
  "keywords": "マネジメント,研修,ベトナム人,管理職,教育,現地化,人材育成"
}}"""

    else:
        prompt = f"""Bạn là copywriter chuyên nghiệp của GOEN Business Training.

【Kiến thức GOEN】
{KNOWLEDGE}

【Loại bài viết】
{type_instruction[content_type]['vi']}

【Chủ đề】
{theme}

Hãy viết bài theo định dạng sau, tối ưu hóa cho SEO và AI Search (AEO):

---TITLE---
（Tiêu đề SEO, dưới 60 ký tự, chứa từ khóa chính）

---SEO_TITLE---
（Tiêu đề cho công cụ tìm kiếm, dưới 60 ký tự）

---META_DESC---
（Mô tả meta, dưới 160 ký tự, chứa từ khóa và CTA）

---FOCUS_KEYWORD---
（Từ khóa trọng tâm cho Rank Math, 1-2 từ）

---BODY---
（Nội dung bài viết theo cấu trúc）
## （Mở đầu: Đặt câu hỏi đồng cảm với độc giả HR Manager）

## （H2-1: Vấn đề cốt lõi）
（~300 từ）

## （H2-2: Góc nhìn và giải pháp của GOEN）
（~300 từ. Sử dụng tự nhiên các khái niệm Mind-Up, bản địa hóa）

## （H2-3: Hành động cụ thể / Kết luận）
（~300 từ）

## Câu hỏi thường gặp
### Q1. （Câu hỏi phổ biến của HR Manager）
A1. （Trả lời ngắn gọn, cụ thể）

### Q2. （Câu hỏi khác）
A2. （Trả lời ngắn gọn）

---CTA---
（Lời kêu gọi hành động của GOEN）

---SCHEMA---
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "（tiêu đề）",
  "description": "（mô tả）",
  "author": {{
    "@type": "Organization",
    "name": "GOEN Business Training"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "GOEN Business Training",
    "url": "https://goen-business.com"
  }},
  "keywords": "quản lý,đào tạo,nhân viên Việt Nam,địa phương hóa,phát triển nhân lực"
}}"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


# =============================
# 記事パース
# =============================
def parse_article(raw):
    result = {
        "title": "", "seo_title": "", "meta_desc": "",
        "focus_keyword": "", "body": "", "cta": "", "schema": ""
    }

    def extract(tag_start, tag_end):
        if tag_start in raw and tag_end in raw:
            return raw.split(tag_start)[1].split(tag_end)[0].strip()
        elif tag_start in raw:
            return raw.split(tag_start)[1].strip()
        return ""

    result["title"] = extract("---TITLE---", "---SEO_TITLE---")
    result["seo_title"] = extract("---SEO_TITLE---", "---META_DESC---")
    result["meta_desc"] = extract("---META_DESC---", "---FOCUS_KEYWORD---")
    result["focus_keyword"] = extract("---FOCUS_KEYWORD---", "---BODY---")
    result["body"] = extract("---BODY---", "---CTA---")
    result["cta"] = extract("---CTA---", "---SCHEMA---")
    result["schema"] = extract("---SCHEMA---", "<<<END>>>")

    return result


# =============================
# 写真をWordPressにアップロード
# =============================
def upload_photo_to_wordpress(photo_url):
    try:
        img_response = requests.get(photo_url, timeout=15)
        if img_response.status_code != 200:
            print(f"⚠️ 写真取得失敗: {photo_url}")
            return None

        credentials = base64.b64encode(f"{WP_USER}:{WP_PASSWORD}".encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Disposition": "attachment; filename=goen-hcmc.jpg",
            "Content-Type": "image/jpeg",
        }

        upload_response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            headers=headers,
            data=img_response.content,
            timeout=30
        )

        if upload_response.status_code in [200, 201]:
            media_id = upload_response.json().get("id")
            print(f"📷 写真アップロード成功: ID={media_id}")
            return media_id
        else:
            print(f"⚠️ 写真アップロード失敗: {upload_response.status_code}")
            return None

    except Exception as e:
        print(f"⚠️ 写真処理エラー: {e}")
        return None


# =============================
# Cloudflare経由でWordPressに投稿
# =============================
def post_via_cloudflare(article, lang="ja", media_id=None):
    # 構造化データをbodyに埋め込む
    schema_block = ""
    if article.get("schema"):
        schema_block = f'\n\n<script type="application/ld+json">\n{article["schema"]}\n</script>'

    content = f'{article["body"]}\n\n---\n{article["cta"]}{schema_block}'

    headers = {
        "Content-Type": "application/json",
        "X-Secret-Key": CF_SECRET_KEY,
    }

    data = {
        "title": article["title"],
        "content": content,
        "status": "draft",
        "meta": {
            "rank_math_focus_keyword": article.get("focus_keyword", ""),
            "rank_math_description": article.get("meta_desc", ""),
            "rank_math_title": article.get("seo_title", article["title"]),
        }
    }

    if media_id:
        data["featured_media"] = media_id

    response = requests.post(
        CLOUDFLARE_WORKER_URL,
        headers=headers,
        json=data,
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 投稿成功 (lang={lang}): ID={result.get('post_id')}, タイトル={article['title']}")
        return True
    else:
        print(f"❌ 投稿失敗 (lang={lang}): {response.status_code} - {response.text}")
        return False


# =============================
# メイン処理
# =============================
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")

# 週番号でテーマを選択（12週ローテーション）
week_number = today.isocalendar()[1]
theme_index = week_number % len(CONTENT_CALENDAR)
theme = CONTENT_CALENDAR[theme_index]
content_type = theme["type"]

print(f"📝 {date_str} の記事を生成・投稿します")
print(f"コンテンツ種別: 種類{content_type} ({'思想・解説' if content_type=='A' else '実践・HOWTO' if content_type=='B' else '匿名事例'})")
print(f"テーマ（日本語）: {theme['ja']}")
print(f"Chủ đề (tiếng Việt): {theme['vi']}")

# 写真をランダム選択してアップロード
photo_url = random.choice(HCMC_PHOTOS)
print(f"\n📷 写真をアップロード中...")
media_id = upload_photo_to_wordpress(photo_url)

# 日本語記事
print("\n--- 日本語記事を生成中 ---")
ja_raw = generate_article(theme["ja"], "ja", content_type)
ja_article = parse_article(ja_raw)
post_via_cloudflare(ja_article, "ja", media_id)

# ベトナム語記事（別の写真）
photo_url_vi = random.choice(HCMC_PHOTOS)
media_id_vi = upload_photo_to_wordpress(photo_url_vi)

print("\n--- ベトナム語記事を生成中 ---")
vi_raw = generate_article(theme["vi"], "vi", content_type)
vi_article = parse_article(vi_raw)
post_via_cloudflare(vi_article, "vi", media_id_vi)

print("\n🎉 本日の記事生成・投稿完了!")

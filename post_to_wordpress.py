import anthropic
import requests
import os
import random
import base64
from datetime import datetime

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLOUDFLARE_WORKER_URL = os.environ["CLOUDFLARE_WORKER_URL"]
CF_SECRET_KEY = os.environ["CF_SECRET_KEY"]
WP_URL = os.environ.get("WP_URL", "https://goen-business.com")
WP_USER = os.environ.get("WP_USER", "kawamurayasuhiro")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

KNOWLEDGE = """
【会社情報】
会社名: GOEN Business Training（代表：川村泰裕、ホーチミン市）
事業: ベトナム進出日系企業向け企業研修・人材育成、日越インターンシップ
ミッション: 「ベトナムの現場に、育つ文化をつくる」
ウェブサイト: https://goen-business.com

【GOENが見てきたベトナム現場のリアル】
- 「研修をやった」で終わっている会社が多い。変わらない理由は研修が「イベント」になっているから
- 「指示待ち」はスタッフの問題ではなく、管理側が「考える余白」を与えていないことが原因
- 「報連相が来ない」のは、悪い情報を上げると怒られる文化が定着しているから
- 駐在員が帰ると組織が止まる会社は「人」に依存していて「仕組み」がない
- 「経営の意図が現場に届かない」×「現場の声が経営に届かない」という双方向断絶が根本問題
- ベトナム人スタッフは「やる気がない」のではなく「何のためにやるのか」が見えていない

【GOENオリジナル定義】

■ 成長とは（3層構造）
  第1層 行動の変化（Doing）: できないことができるようになること
  第2層 メタ認知の獲得（Knowing）: なぜできるようになったかを自分の言葉で説明できること
  第3層 意味構造の変容（Being）: 世界の見え方・意味のつくり方そのものが変わること
  ※研修でよくあるのは「第1層だけ」の変化。GOENは第3層まで目指す。

■ 育成とは
  「成長の3層が起きやすい環境と関係性を、意図的に設計すること」
  教えること≠育成。大人は気づいたときだけ深く学ぶ（ノールズのアンドラゴジー）。
  育成の4要素: 安全な場 × 自律的動機（うまみの設計）× 意味が見える構造 × 組織として学ぶ仕組み

■ Mind-Up（マインドアップ）
  目線を上げ続けること。「言われたことをやる」から「なぜやるのかを理解して動く」へ。
  ドゥエックの成長マインドセット理論と直結する。

■ 量と筋のOS理論
  「量のOS」= 目の前の現実・損益・影響の大きさで判断する思考様式。ベトナムに多い。
  「筋のOS」= 原理原則・整合性・べき論で判断する思考様式。日本に多い。
  重要: これは優劣ではなく「異なるOS」。OSの違いを知ることで管理側の摩擦が激減する。

■ 現地化（ローカライゼーション）の本質
  「日本のやり方をベトナム語に翻訳する」ことではない。
  現地スタッフが自律的に動ける状態をつくること。任せているようで任せていない状態を変えること。

■ GOENが使う言葉
  「育つ文化をつくる」「研修をイベントで終わらせない」「任せているようで任せていない」
  「目線を上げ続ける」「自分ごととして捉える」「言語化・見える化」「気づきを引き出す」

【SEOキーワード】
メイン: マネジメント、研修、ベトナム人、管理職、教育
サブ: 現地化、人材育成、日系企業、ホーチミン、組織文化

【ターゲット読者】
日本語: 在越日系企業の社長・管理部長。「また研修やっても変わらない」と半信半疑な人。「駐在員が帰ったら組織が止まる」という不安を持つ人。
ベトナム語: 日系企業のHRマネージャー（40代女性）。現場と経営層の間で苦労している人。

【トーン】
日本語: 現場感・共感ベース。具体的な場面描写から入る。上から目線禁止。問いかけを多用。
ベトナム語: 親しみやすく実用的。先輩HRが後輩に教える感覚。翌日から使えるアクションを必ず入れる。

【CTA】
日本語: GOENでは、在越日系企業の人材育成・現地化推進を専門にサポートしています。「うちの現場を見てほしい」「まず話だけ聞きたい」——どちらでも大歓迎です。まずは無料相談からどうぞ。▶ https://goen-business.com/lien-he/
ベトナム語: GOEN chuyên hỗ trợ đào tạo và phát triển nhân lực cho doanh nghiệp Nhật Bản tại Việt Nam. Dù bạn chỉ muốn tham khảo hay đang tìm giải pháp cụ thể — hãy liên hệ với chúng tôi. Tư vấn miễn phí: https://goen-business.com/lien-he/
"""

CONTENT_CALENDAR = [
    {"type": "A", "ja": "現地化とは何か。「日本のやり方を翻訳する」ことではない",
     "vi": "Bản địa hóa thực sự là gì? Không chỉ là dịch cách làm của Nhật"},
    {"type": "B", "ja": "「指示待ち人材」を変える3つの問いかけ。管理職が今日から使えるフレーズ",
     "vi": "3 câu hỏi giúp nhân viên thoát khỏi tư duy chờ lệnh"},
    {"type": "C", "ja": "【事例】研修をイベントで終わらせなかった製造業A社の3年間",
     "vi": "【Case study】3 năm không để đào tạo chỉ là sự kiện của công ty sản xuất A"},
    {"type": "A", "ja": "Mind-Upとは何か。目線を上げ続ける組織のつくり方",
     "vi": "Mind-Up là gì? Xây dựng tổ chức không ngừng nâng tầm tư duy"},
    {"type": "B", "ja": "「報連相」が上がってこない本当の理由と今すぐできる対策",
     "vi": "Vì sao nhân viên không báo cáo? Giải pháp thực tế từ ngày hôm nay"},
    {"type": "C", "ja": "【事例】駐在員ゼロでも回る組織をつくったB社の現地化戦略",
     "vi": "【Case study】Chiến lược bản địa hóa của công ty B vận hành tốt không cần người Nhật"},
    {"type": "A", "ja": "量と筋のOS——なぜ日越間でこんなにもすれ違うのか",
     "vi": "OS 'Ryo' và 'Suji' – Tại sao người Nhật và người Việt hay hiểu lầm nhau?"},
    {"type": "B", "ja": "現地マネージャーへの権限委譲。失敗しない5つのステップ",
     "vi": "5 bước giao quyền cho quản lý người Việt mà không sợ thất bại"},
    {"type": "C", "ja": "【事例】双方向断絶を乗り越えたC社。経営と現場をつないだ仕組みとは",
     "vi": "【Case study】Công ty C đã kết nối kinh doanh và thực tế như thế nào?"},
    {"type": "A", "ja": "成長とは何か。育成とは何か。GOENが現場から導いた定義",
     "vi": "Tăng trưởng là gì? Đào tạo là gì? Định nghĩa từ thực tế của GOEN"},
    {"type": "B", "ja": "QCとトヨタ式8ステップ。ベトナム現場に定着させる導入のコツ",
     "vi": "QC và 8 bước Toyota. Bí quyết triển khai hiệu quả tại Việt Nam"},
    {"type": "C", "ja": "【事例】「任せているようで任せていない」を脱したD社の変化",
     "vi": "【Case study】Công ty D đã thoát khỏi tình trạng giao việc nhưng không thực sự tin tưởng"},
]

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

def generate_article(theme, lang, content_type):
    type_ja = {"A": "思想・解説コラム。GOENの核心思想（成長の3層・Mind-Up・量と筋・現地化）を軸に深い洞察を書く。抽象論禁止。必ず具体的な場面描写を入れる。",
               "B": "実践・HOWTOコラム。明日から現場で使える手法・フレーズ・ステップを書く。読んだ翌日から使えるアクションを必ず入れる。",
               "C": "匿名事例コラム。「ある製造業の日系企業A社」という形でGOENが支援した企業の変化を描く。Before/Afterを明確に。社名は絶対に出さない。"}
    type_vi = {"A": "Bài tư tưởng. Giải thích sâu triết lý GOEN cho HR Manager. Luôn bắt đầu bằng tình huống cụ thể.",
               "B": "Bài hướng dẫn. Cung cấp bước cụ thể, câu mẫu dùng được ngay. Luôn có 1 hành động có thể làm ngay hôm sau.",
               "C": "Case study ẩn danh. Mô tả sự thay đổi của 'Công ty A'. Rõ Before/After. Không nêu tên thật."}

    if lang == "ja":
        prompt = f"""あなたはGOEN Business Trainingの専属コンテンツライターです。

【GOENナレッジ】
{KNOWLEDGE}

【記事種別】{type_ja[content_type]}

【テーマ】{theme}

【絶対に守るルール】
1. 最初の2〜3行で読者を引き込む。「あるある」な場面描写から始める
   例：「月曜朝の朝礼。『何か問題はありますか？』という問いに、静まり返る会議室——」
2. 抽象論・一般論禁止。必ず「具体的な場面」「実際の会話例」「数字」を入れる
3. GOENの言葉（Mind-Up・現地化・量と筋・育つ文化・成長の3層）を自然に使う
4. 読者が「これ、うちのことだ」と感じる瞬間を必ず1箇所つくる
5. 写真挿入位置として【PHOTO】を本文中に2箇所入れる（H2見出しの直後）

---TITLE---
（SEOタイトル。32文字以内。メインキーワードを含める）
---SEO_TITLE---
（検索エンジン用タイトル。32文字以内）
---META_DESC---
（メタディスクリプション。120文字以内）
---FOCUS_KEYWORD---
（Rank Math用フォーカスキーワード。1〜2語）
---BODY---
## （リード：場面描写から始まる問いかけ）

## （H2-1：問題の本質）
【PHOTO】
（本文300字。具体的な場面・会話例を含む）

## （H2-2：GOENの視点と解決策）
（本文300字。GOENキーワードを自然に使う）

## （H2-3：具体的なアクション）
【PHOTO】
（本文300字。明日から使えるアクションを含む）

## よくある質問
### Q1. （読者がよく持つ具体的な疑問）
A1. （簡潔・具体的な回答）
### Q2. （別の具体的な疑問）
A2. （簡潔・具体的な回答）
---CTA---
（GOENのCTAを使う）
---SCHEMA---
{{"@context":"https://schema.org","@type":"Article","headline":"タイトル","description":"メタディスクリプション","author":{{"@type":"Organization","name":"GOEN Business Training"}},"publisher":{{"@type":"Organization","name":"GOEN Business Training","url":"https://goen-business.com"}},"keywords":"マネジメント,研修,ベトナム人,管理職,教育,現地化,人材育成"}}"""
    else:
        prompt = f"""Bạn là copywriter chuyên nghiệp của GOEN Business Training.

【Kiến thức GOEN】
{KNOWLEDGE}

【Loại bài】{type_vi[content_type]}
【Chủ đề】{theme}

【Quy tắc】
1. Mở đầu bằng tình huống cụ thể gần gũi với HR Manager
2. Luôn có ví dụ thực tế, con số, câu thoại cụ thể
3. Dùng tự nhiên: Mind-Up, bản địa hóa, OS lượng-cân
4. Có 1 hành động cụ thể làm được ngay hôm sau
5. Chèn 【PHOTO】 vào 2 vị trí sau tiêu đề H2

---TITLE---
---SEO_TITLE---
---META_DESC---
---FOCUS_KEYWORD---
---BODY---
## Mở đầu
## H2-1
【PHOTO】
## H2-2
## H2-3
【PHOTO】
## Câu hỏi thường gặp
### Q1.
A1.
### Q2.
A2.
---CTA---
---SCHEMA---
{{"@context":"https://schema.org","@type":"Article","headline":"tiêu đề","description":"mô tả","author":{{"@type":"Organization","name":"GOEN Business Training"}},"publisher":{{"@type":"Organization","name":"GOEN Business Training","url":"https://goen-business.com"}},"keywords":"quản lý,đào tạo,nhân viên Việt Nam,địa phương hóa,phát triển nhân lực"}}"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def parse_article(raw):
    result = {"title":"","seo_title":"","meta_desc":"","focus_keyword":"","body":"","cta":"","schema":""}
    def extract(s, e):
        if s in raw:
            part = raw.split(s)[1]
            return part.split(e)[0].strip() if e in part else part.strip()
        return ""
    result["title"] = extract("---TITLE---","---SEO_TITLE---")
    result["seo_title"] = extract("---SEO_TITLE---","---META_DESC---")
    result["meta_desc"] = extract("---META_DESC---","---FOCUS_KEYWORD---")
    result["focus_keyword"] = extract("---FOCUS_KEYWORD---","---BODY---")
    result["body"] = extract("---BODY---","---CTA---")
    result["cta"] = extract("---CTA---","---SCHEMA---")
    result["schema"] = extract("---SCHEMA---","<<<END>>>")
    return result

def upload_photo(photo_url):
    try:
        headers = {"Content-Type":"application/json","X-Secret-Key":CF_SECRET_KEY,"X-Action":"upload_media","X-Image-Url":photo_url}
        r = requests.post(CLOUDFLARE_WORKER_URL, headers=headers, json={}, timeout=30)
        if r.status_code == 200:
            mid = r.json().get("media_id")
            print(f"📷 写真アップロード成功: ID={mid}")
            return mid
        print(f"⚠️ 写真アップロード失敗: {r.status_code}")
        return None
    except Exception as e:
        print(f"⚠️ 写真エラー: {e}")
        return None

def insert_photos(body, photo_urls):
    for url in photo_urls:
        img_tag = f'\n\n<figure class="wp-block-image size-large"><img src="{url}" alt="ホーチミン ベトナム 日系企業 研修 人材育成" /></figure>\n\n'
        body = body.replace("【PHOTO】", img_tag, 1)
    return body

def post_article(article, lang="ja", media_id=None, inline_photos=None):
    schema_block = f'\n\n<script type="application/ld+json">\n{article["schema"]}\n</script>' if article.get("schema") else ""
    body = insert_photos(article["body"], inline_photos) if inline_photos else article["body"]
    content = f'{body}\n\n---\n{article["cta"]}{schema_block}'
    data = {"title":article["title"],"content":content,"status":"draft",
            "meta":{"rank_math_focus_keyword":article.get("focus_keyword",""),
                    "rank_math_description":article.get("meta_desc",""),
                    "rank_math_title":article.get("seo_title",article["title"])}}
    if media_id:
        data["featured_media"] = media_id
    r = requests.post(CLOUDFLARE_WORKER_URL,
                      headers={"Content-Type":"application/json","X-Secret-Key":CF_SECRET_KEY},
                      json=data, timeout=30)
    if r.status_code == 200:
        result = r.json()
        print(f"✅ 投稿成功 (lang={lang}): ID={result.get('post_id')}, タイトル={article['title']}")
        return True
    print(f"❌ 投稿失敗 (lang={lang}): {r.status_code} - {r.text}")
    return False

today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
week_number = today.isocalendar()[1]
theme = CONTENT_CALENDAR[week_number % len(CONTENT_CALENDAR)]
content_type = theme["type"]
type_label = {'A':'思想・解説','B':'実践・HOWTO','C':'匿名事例'}[content_type]

print(f"📝 {date_str} の記事を生成・投稿します")
print(f"コンテンツ種別: 種類{content_type}（{type_label}）")
print(f"テーマ（日本語）: {theme['ja']}")
print(f"Chủ đề (tiếng Việt): {theme['vi']}")

selected = random.sample(HCMC_PHOTOS, min(3, len(HCMC_PHOTOS)))
print(f"\n📷 アイキャッチ写真をアップロード中...")
media_id = upload_photo(selected[0])

print("\n--- 日本語記事を生成中 ---")
ja_article = parse_article(generate_article(theme["ja"], "ja", content_type))
post_article(ja_article, "ja", media_id, selected[1:3])

selected_vi = random.sample(HCMC_PHOTOS, min(3, len(HCMC_PHOTOS)))
media_id_vi = upload_photo(selected_vi[0])

print("\n--- ベトナム語記事を生成中 ---")
vi_article = parse_article(generate_article(theme["vi"], "vi", content_type))
post_article(vi_article, "vi", media_id_vi, selected_vi[1:3])

print("\n🎉 本日の記事生成・投稿完了!")

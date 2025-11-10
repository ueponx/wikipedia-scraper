# Wikipedia Scraper

Wikipediaから記事情報を取得し、Markdown・JSON・テキスト形式で保存するコマンドラインツールです。

## 📚 概要
以下のリンクに解説をまとめています。また、このドキュメントはLLMによって自動生成されたものです。

https://uepon.hatenadiary.com/entry/2025/11/10/233001

## ✨ 特徴

- 🚀 **高速**: uvを使った高速なパッケージ管理
- 📝 **多形式対応**: Markdown、JSON、テキスト形式で保存可能
- 🌍 **多言語対応**: 日本語版・英語版など複数言語のWikipediaに対応
- 📦 **包括的なデータ取得**: 要約、本文、カテゴリ、リンク、セクション構造、参照情報を取得
- 🔄 **一括処理**: 複数記事を一度に取得可能
- 📊 **進捗表示**: tqdmによる視覚的な進捗バー

## 📋 取得できる情報

- ページタイトル、ページID、URL
- 記事の要約と全文
- カテゴリ情報
- セクション構造（階層付き）
- 内部リンク（最大100件）
- 参照文献・脚注

## 🔧 インストール

### 前提条件

- Python 3.10以上
- uv（Pythonパッケージマネージャー）

### uvのインストール

```bash
# macOS/Linux/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# インストール後、シェルを再起動または以下を実行
source ~/.bashrc  # または ~/.zshrc
```

### プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/ueponx/wikipedia-scraper.git
cd wikipedia-scraper

# 依存関係をインストール（仮想環境の作成も自動で行われます）
uv sync
```

## 🚀 使い方

### 実行方法

uvを使ったプロジェクトでは、以下の2つの方法でスクリプトを実行できます：

```bash
# 方法1: uv runを使う（推奨）
uv run wikipedia_scraper.py "Python"

# 方法2: 仮想環境を有効化して実行
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python wikipedia_scraper.py "Python"
```

以降の例では、シンプルな`python`コマンド形式で記載しますが、`uv run`でも実行できます。

### 基本的な使用方法

#### 単一記事の取得（Markdown形式）

```bash
python wikipedia_scraper.py "Python"
```

#### 異なる形式で保存

```bash
# JSON形式
python wikipedia_scraper.py "機械学習" --format json

# テキスト形式
python wikipedia_scraper.py "人工知能" --format text

# すべての形式で保存
python wikipedia_scraper.py "データサイエンス" --format all
```

#### 複数記事の一括取得

```bash
# keywords.txtを作成
cat > keywords.txt << EOF
Python
機械学習
人工知能
データサイエンス
Node-RED
EOF

# 一括取得
python wikipedia_scraper.py --inputs keywords.txt
```

#### 英語版Wikipediaから取得

```bash
python wikipedia_scraper.py "Python" --lang en
```

## 📖 コマンドオプション

```
usage: wikipedia_scraper.py [title] [options]

Wikipedia記事取得ツール

positional arguments:
  title                 Wikipedia記事のタイトル

optional arguments:
  --inputs INPUT_FILE   検索キーワードが書かれたテキストファイル（1行1キーワード）
  --format {markdown,json,text,all}
                        出力形式（デフォルト: markdown）
  --lang LANGUAGE       言語コード（デフォルト: ja）
  -h, --help            ヘルプメッセージを表示
```

### 使用例

```bash
# 単一記事をMarkdown形式で取得（デフォルト）
python wikipedia_scraper.py "Python"

# 単一記事をJSON形式で取得
python wikipedia_scraper.py "機械学習" --format json

# すべての形式で保存
python wikipedia_scraper.py "Python" --format all

# 複数記事を一括取得
python wikipedia_scraper.py --inputs keywords.txt

# 英語版Wikipediaから取得
python wikipedia_scraper.py "Python" --lang en

# 複数記事をJSON形式で一括取得
python wikipedia_scraper.py --inputs keywords.txt --format json
```

## 📂 出力形式

### Markdown形式

```markdown
# Python

**ページID**: 123456
**URL**: https://ja.wikipedia.org/wiki/Python
**言語**: ja
**取得日時**: 2024-11-10T10:30:45.123456

---

## 要約

Pythonは、汎用のプログラミング言語である...

---

## カテゴリ

- Category:プログラミング言語
- Category:オブジェクト指向言語
...
```

### JSON形式

```json
{
  "title": "Python",
  "pageid": 123456,
  "url": "https://ja.wikipedia.org/wiki/Python",
  "language": "ja",
  "timestamp": "2024-11-10T10:30:45.123456",
  "summary": "Pythonは、汎用のプログラミング言語である...",
  "full_text": "...",
  "categories": [...],
  "sections": [...],
  "links": {...},
  "references": {...}
}
```

### テキスト形式

```
タイトル: Python
ページID: 123456
URL: https://ja.wikipedia.org/wiki/Python
言語: ja
取得日時: 2024-11-10T10:30:45.123456
======================================================================

【要約】
Pythonは、汎用のプログラミング言語である...
```

## 🎯 活用例

### 1. 研究のための情報収集

```bash
# 研究キーワードを準備
cat > research_keywords.txt << EOF
大規模言語モデル
Transformer
BERT
GPT
注意機構
EOF

# 全形式で保存
python wikipedia_scraper.py --inputs research_keywords.txt --format all
```

### 2. RAGシステムのナレッジベース構築

取得したMarkdownファイルをLangChainやLlamaIndexで読み込み、RAG（Retrieval-Augmented Generation）システムのナレッジベースとして活用できます。

```python
from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader('./output', glob="**/*.md")
documents = loader.load()
```

### 3. 多言語での情報比較

```bash
# 日本語版
python wikipedia_scraper.py "機械学習" --format json

# 英語版
python wikipedia_scraper.py "Machine learning" --lang en --format json
```

### 4. 定期的な情報更新（cron）

```bash
# cronに登録して毎日更新
0 2 * * * cd /path/to/wikipedia-scraper && source .venv/bin/activate && python wikipedia_scraper.py --inputs keywords.txt
```

## 🛠️ 開発環境

### 動作確認環境

- Python 3.10+
- uv 0.5.0+
- Wikipedia-API 0.7.1+
- tqdm 4.67.1+

### 開発用セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/ueponx/wikipedia-scraper.git
cd wikipedia-scraper

# 依存関係をインストール（仮想環境の作成も自動で行われます）
uv sync

# 実行
uv run wikipedia_scraper.py "Python"
# または
# source .venv/bin/activate
# python wikipedia_scraper.py "Python"
```

## 🐛 トラブルシューティング

### `ModuleNotFoundError: No module named 'wikipediaapi'`

仮想環境が有効化されていないか、ライブラリがインストールされていない可能性があります。

```bash
# 依存関係を再インストール
uv sync
```

### 記事が見つからない

記事タイトルが正確でない可能性があります。Wikipediaで記事を開き、ページ上部の見出しを確認してください。

- ❌ `python` → ⭕ `Python`
- ❌ `機械 学習` → ⭕ `機械学習`

### 文字化けが発生する

ファイルはUTF-8で保存されています。ファイルを開く際は、UTF-8対応のエディタを使用してください。

## 📝 ライセンス

MIT License

## 🙏 謝辞

このプロジェクトは以下のオープンソースプロジェクトを使用しています：

- [wikipedia-api](https://github.com/martin-majlis/Wikipedia-API) - Wikipedia APIクライアント
- [tqdm](https://github.com/tqdm/tqdm) - プログレスバーライブラリ
- [uv](https://github.com/astral-sh/uv) - 高速Pythonパッケージマネージャー

## 📚 関連リンク

- [Wikipedia-API ドキュメント](https://wikipedia-api.readthedocs.io/)
- [uv 公式ドキュメント](https://docs.astral.sh/uv/)
- [Python argparse ドキュメント](https://docs.python.org/ja/3/library/argparse.html)

---

**Star ⭐ をいただけると励みになります！**

"""
Wikipedia情報取得ツール

Wikipediaから記事を検索し、要約・本文・カテゴリ・リンク・参照など
すべての利用可能なデータを取得するコマンドラインツール
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import wikipediaapi
from tqdm import tqdm


class WikipediaScraper:
    """Wikipedia情報取得クラス"""
    
    def __init__(self, language='ja'):
        """
        初期化
        
        Args:
            language (str): 言語コード (デフォルト: 'ja')
        """
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='WikipediaScraper/2.0',
            language=language
        )
        self.language = language
        self.output_dir = Path('./output')
        self.output_dir.mkdir(exist_ok=True)
    
    def search_page(self, title):
        """
        Wikipedia記事を検索
        
        Args:
            title (str): 記事タイトル
            
        Returns:
            wikipediaapi.WikipediaPage or None: 記事ページ
        """
        page = self.wiki.page(title)
        if page.exists():
            return page
        else:
            print(f"警告: 記事 '{title}' が見つかりませんでした")
            return None
    
    def get_all_data(self, title):
        """
        記事のすべてのデータを取得
        
        Args:
            title (str): 記事タイトル
            
        Returns:
            dict: すべてのデータを含む辞書
        """
        page = self.search_page(title)
        if not page:
            return None
        
        data = {
            'title': page.title,
            'pageid': page.pageid,
            'url': page.fullurl,
            'canonical_url': page.canonicalurl,
            'language': self.language,
            'timestamp': datetime.now().isoformat(),
            'summary': page.summary,
            'full_text': page.text,
            'categories': self._get_categories(page),
            'sections': self._get_sections(page),
            'links': self._get_links(page),
            'references': self._get_references(page),
            'backlinks': [],  # APIの制限により取得できない
        }
        
        return data
    
    def _get_categories(self, page):
        """
        カテゴリ情報を取得
        
        Args:
            page: WikipediaPage オブジェクト
            
        Returns:
            list: カテゴリのリスト
        """
        try:
            return [cat for cat in page.categories.keys()]
        except Exception as e:
            print(f"  カテゴリ取得エラー: {e}")
            return []
    
    def _get_sections(self, page, section=None, level=0):
        """
        セクション構造を再帰的に取得
        
        Args:
            page: WikipediaPage オブジェクトまたはセクション
            section: 現在のセクション
            level: セクションの階層レベル
            
        Returns:
            list: セクション情報のリスト
        """
        sections = []
        
        if section is None:
            section = page
        
        for s in section.sections:
            section_info = {
                'title': s.title,
                'level': level,
                'text': s.text[:500] + '...' if len(s.text) > 500 else s.text,
                'subsections': self._get_sections(page, s, level + 1)
            }
            sections.append(section_info)
        
        return sections
    
    def _get_links(self, page):
        """
        リンク情報を取得
        
        Args:
            page: WikipediaPage オブジェクト
            
        Returns:
            dict: 内部リンクと外部リンクのリスト
        """
        try:
            internal_links = list(page.links.keys())[:100]  # 最初の100件のみ
            return {
                'internal_links': internal_links,
                'internal_links_count': len(page.links)
            }
        except Exception as e:
            print(f"  リンク取得エラー: {e}")
            return {
                'internal_links': [],
                'internal_links_count': 0
            }
    
    def _get_references(self, page):
        """
        参照文献情報を取得（本文から抽出）
        
        Args:
            page: WikipediaPage オブジェクト
            
        Returns:
            dict: 参照情報
        """
        text = page.text
        references_section = ""
        
        for section in page.sections:
            if any(keyword in section.title.lower() for keyword in ['参考', '脚注', '出典', 'references', 'notes']):
                references_section = section.text
                break
        
        return {
            'has_references_section': bool(references_section),
            'references_text': references_section[:1000] if references_section else ""
        }
    
    def save_to_markdown(self, title, data):
        """
        データをMarkdown形式で保存
        
        Args:
            title (str): 記事タイトル
            data (dict): 保存するデータ
        """
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        filename = f"{safe_title}_complete.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # ヘッダー情報
            f.write(f"# {data['title']}\n\n")
            f.write(f"**ページID**: {data['pageid']}  \n")
            f.write(f"**URL**: {data['url']}  \n")
            f.write(f"**言語**: {data['language']}  \n")
            f.write(f"**取得日時**: {data['timestamp']}  \n\n")
            f.write("---\n\n")
            
            # 要約
            f.write("## 要約\n\n")
            f.write(f"{data['summary']}\n\n")
            f.write("---\n\n")
            
            # カテゴリ
            if data['categories']:
                f.write("## カテゴリ\n\n")
                for cat in data['categories'][:20]:
                    f.write(f"- {cat}\n")
                if len(data['categories']) > 20:
                    f.write(f"\n（他 {len(data['categories']) - 20} 件）\n")
                f.write("\n---\n\n")
            
            # セクション構造
            if data['sections']:
                f.write("## セクション構造\n\n")
                self._write_sections_markdown(f, data['sections'])
                f.write("\n---\n\n")
            
            # 本文
            f.write("## 本文\n\n")
            f.write(f"{data['full_text']}\n\n")
            f.write("---\n\n")
            
            # リンク情報
            f.write("## リンク情報\n\n")
            f.write(f"**内部リンク総数**: {data['links']['internal_links_count']}\n\n")
            if data['links']['internal_links']:
                f.write("### 主要な内部リンク（最大100件）\n\n")
                for link in data['links']['internal_links'][:50]:
                    f.write(f"- {link}\n")
                if len(data['links']['internal_links']) > 50:
                    f.write(f"\n（他 {len(data['links']['internal_links']) - 50} 件）\n")
            f.write("\n---\n\n")
            
            # 参照情報
            if data['references']['has_references_section']:
                f.write("## 参照・脚注\n\n")
                f.write(f"{data['references']['references_text']}\n\n")
        
        print(f"✓ Markdown保存完了: {filepath}")
    
    def save_to_json(self, title, data):
        """
        データをJSON形式で保存
        
        Args:
            title (str): 記事タイトル
            data (dict): 保存するデータ
        """
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        filename = f"{safe_title}_complete.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON保存完了: {filepath}")
    
    def save_to_text(self, title, data):
        """
        データをテキスト形式で保存
        
        Args:
            title (str): 記事タイトル
            data (dict): 保存するデータ
        """
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        filename = f"{safe_title}_complete.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"タイトル: {data['title']}\n")
            f.write(f"ページID: {data['pageid']}\n")
            f.write(f"URL: {data['url']}\n")
            f.write(f"言語: {data['language']}\n")
            f.write(f"取得日時: {data['timestamp']}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("【要約】\n")
            f.write(data['summary'] + "\n\n")
            f.write("=" * 70 + "\n\n")
            
            if data['categories']:
                f.write("【カテゴリ】\n")
                for cat in data['categories']:
                    f.write(f"  - {cat}\n")
                f.write("\n" + "=" * 70 + "\n\n")
            
            f.write("【本文】\n")
            f.write(data['full_text'] + "\n\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"【リンク情報】\n")
            f.write(f"内部リンク数: {data['links']['internal_links_count']}\n\n")
        
        print(f"✓ テキスト保存完了: {filepath}")
    
    def _write_sections_markdown(self, f, sections, indent=0):
        """
        セクション情報をMarkdown形式で書き込み
        
        Args:
            f: ファイルオブジェクト
            sections: セクション情報のリスト
            indent: インデント レベル
        """
        for section in sections:
            prefix = "  " * indent + "- "
            f.write(f"{prefix}**{section['title']}** (レベル {section['level']})\n")
            if section['subsections']:
                self._write_sections_markdown(f, section['subsections'], indent + 1)
    
    def process_single(self, title, output_format='markdown'):
        """
        単一の記事を処理
        
        Args:
            title (str): 記事タイトル
            output_format (str): 出力形式 ('markdown', 'json', 'text', 'all')
        """
        print(f"\n検索中: {title}")
        
        data = self.get_all_data(title)
        
        if data:
            if output_format in ['markdown', 'all']:
                self.save_to_markdown(title, data)
            if output_format in ['json', 'all']:
                self.save_to_json(title, data)
            if output_format in ['text', 'all']:
                self.save_to_text(title, data)
        else:
            print(f"✗ 記事 '{title}' の取得に失敗しました")
    
    def process_multiple(self, input_file, output_format='markdown'):
        """
        複数の記事を一括処理
        
        Args:
            input_file (str): 検索キーワードが書かれたテキストファイル
            output_format (str): 出力形式
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip()]
            
            print(f"\n{len(titles)}件の記事を処理します...\n")
            
            for title in tqdm(titles, desc="記事取得中", unit="記事"):
                self.process_single(title, output_format)
            
            print(f"\n完了! {len(titles)}件の記事を処理しました")
        
        except FileNotFoundError:
            print(f"エラー: ファイル '{input_file}' が見つかりません")
        except Exception as e:
            print(f"エラー: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Wikipediaから記事のすべてのデータを取得するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
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
        """
    )
    
    parser.add_argument(
        'title',
        nargs='?',
        help='Wikipedia記事のタイトル'
    )
    
    parser.add_argument(
        '--inputs',
        type=str,
        help='検索キーワードが書かれたテキストファイル(1行1キーワード)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['markdown', 'json', 'text', 'all'],
        default='markdown',
        help='出力形式 (デフォルト: markdown)'
    )
    
    parser.add_argument(
        '--lang',
        type=str,
        default='ja',
        help='言語コード (デフォルト: ja)'
    )
    
    args = parser.parse_args()
    
    # 引数チェック
    if not args.title and not args.inputs:
        parser.print_help()
        print("\nエラー: 記事タイトルまたは--inputsオプションを指定してください")
        return
    
    # スクレイパーの初期化
    scraper = WikipediaScraper(language=args.lang)
    
    # 処理実行
    if args.inputs:
        scraper.process_multiple(args.inputs, args.format)
    else:
        scraper.process_single(args.title, args.format)


if __name__ == '__main__':
    main()

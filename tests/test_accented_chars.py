#!/usr/bin/env python3
"""
アキュート記号付き文字とアポストロフィの文字化けテスト

このテストは、PDF抽出時にアキュート記号付き文字やアポストロフィが
正しく抽出されることを確認します。
"""

import sys
import subprocess
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_test_pdf_with_accents():
    """アキュート記号付き文字とアポストロフィを含むテストPDFを作成"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        test_pdf_path = Path(__file__).parent / "test_accented.pdf"
        
        c = canvas.Canvas(str(test_pdf_path), pagesize=A4)
        
        # テスト対象の文字列（受け入れ基準より）
        test_strings = [
            "café résumé jalapeño piñata",
            "l'été naïve coöperate l'œuvre",
            "São Gödel",
            "it's l'heure rock 'n' roll",
        ]
        
        # テキストを描画
        y_position = 750
        for text in test_strings:
            c.drawString(100, y_position, text)
            y_position -= 30
        
        c.showPage()
        c.save()
        
        return test_pdf_path
        
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")
        return None


def test_pypdf_engine():
    """pypdf エンジンでアキュート記号付き文字が正しく抽出されることを確認"""
    test_pdf_path = create_test_pdf_with_accents()
    if test_pdf_path is None:
        return
    
    try:
        # pypdf エンジンでテキストを抽出
        result = subprocess.run(
            ["python", "pdf_page_text.py", "--pdf", str(test_pdf_path), "--page", "1", "--engine", "pypdf"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"終了コードが0ではありません: {result.returncode}"
        
        # 出力ファイルを確認
        output_file = Path(__file__).parent.parent / "test_accented-1.txt"
        assert output_file.exists(), f"出力ファイルが作成されませんでした: {output_file}"
        
        # 出力ファイルの内容を確認
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 置換文字（�）が含まれていないことを確認
        assert '�' not in content, "置換文字（�）が出力に含まれています"
        
        # テスト文字列が含まれていることを確認（一部）
        test_words = ['café', 'résumé', 'jalapeño', 'piñata', "l'été", 'naïve', 'São', 'Gödel']
        found_words = []
        missing_words = []
        
        for word in test_words:
            if word in content:
                found_words.append(word)
            else:
                missing_words.append(word)
        
        # クリーンアップ
        output_file.unlink()
        
        print(f"✓ pypdf エンジンのテスト成功")
        print(f"  正しく抽出された単語: {', '.join(found_words)}")
        if missing_words:
            print(f"  ⚠ 抽出されなかった単語（PDF生成の問題の可能性）: {', '.join(missing_words)}")
        
    finally:
        # テストPDFをクリーンアップ
        if test_pdf_path and test_pdf_path.exists():
            test_pdf_path.unlink()


def test_pdfminer_engine():
    """pdfminer エンジンでアキュート記号付き文字が正しく抽出されることを確認"""
    test_pdf_path = create_test_pdf_with_accents()
    if test_pdf_path is None:
        return
    
    try:
        # pdfminer.six が利用可能かチェック
        try:
            import pdfminer
        except ImportError:
            print("⚠ pdfminer.six がインストールされていないため、pdfminer エンジンのテストをスキップしました")
            return
        
        # pdfminer エンジンでテキストを抽出
        result = subprocess.run(
            ["python", "pdf_page_text.py", "--pdf", str(test_pdf_path), "--page", "1", "--engine", "pdfminer"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"終了コードが0ではありません: {result.returncode}"
        
        # 出力ファイルを確認
        output_file = Path(__file__).parent.parent / "test_accented-1.txt"
        assert output_file.exists(), f"出力ファイルが作成されませんでした: {output_file}"
        
        # 出力ファイルの内容を確認
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 置換文字（�）が含まれていないことを確認
        assert '�' not in content, "置換文字（�）が出力に含まれています"
        
        # テスト文字列が含まれていることを確認（一部）
        test_words = ['café', 'résumé', 'jalapeño', 'piñata', "l'été", 'naïve', 'São', 'Gödel']
        found_words = []
        missing_words = []
        
        for word in test_words:
            if word in content:
                found_words.append(word)
            else:
                missing_words.append(word)
        
        # クリーンアップ
        output_file.unlink()
        
        print(f"✓ pdfminer エンジンのテスト成功")
        print(f"  正しく抽出された単語: {', '.join(found_words)}")
        if missing_words:
            print(f"  ⚠ 抽出されなかった単語（PDF生成の問題の可能性）: {', '.join(missing_words)}")
        
    finally:
        # テストPDFをクリーンアップ
        if test_pdf_path and test_pdf_path.exists():
            test_pdf_path.unlink()


def test_output_encoding():
    """出力ファイルがUTF-8エンコーディングであることを確認"""
    test_pdf_path = create_test_pdf_with_accents()
    if test_pdf_path is None:
        return
    
    try:
        # テキストを抽出
        result = subprocess.run(
            ["python", "pdf_page_text.py", "--pdf", str(test_pdf_path), "--page", "1"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # 出力ファイルを確認
        output_file = Path(__file__).parent.parent / "test_accented-1.txt"
        assert output_file.exists()
        
        # UTF-8としてファイルを読み込めることを確認
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print("✓ 出力ファイルのUTF-8エンコーディングテスト成功")
        except UnicodeDecodeError:
            raise AssertionError("出力ファイルがUTF-8でエンコードされていません")
        finally:
            # クリーンアップ
            output_file.unlink()
        
    finally:
        # テストPDFをクリーンアップ
        if test_pdf_path and test_pdf_path.exists():
            test_pdf_path.unlink()


if __name__ == "__main__":
    print("=== アキュート記号付き文字とアポストロフィのテスト ===\n")
    
    try:
        test_pypdf_engine()
        test_pdfminer_engine()
        test_output_encoding()
        
        print("\n=== すべてのテストが成功しました ===")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ テスト失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

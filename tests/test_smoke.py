#!/usr/bin/env python3
"""
pdf_page_text.py のスモークテスト

基本的な動作を確認するための最小限のテスト
"""

import sys
import subprocess
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_help_option():
    """ヘルプオプションが正常に動作することを確認"""
    result = subprocess.run(
        ["python", "pdf_page_text.py", "--help"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "PDFファイルの指定ページからテキストを抽出" in result.stdout
    print("✓ ヘルプオプションのテスト成功")


def test_missing_pdf_file():
    """存在しないPDFファイルを指定した場合のエラーハンドリングを確認"""
    result = subprocess.run(
        ["python", "pdf_page_text.py", "--pdf", "nonexistent.pdf", "--page", "1"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "PDFファイルが見つかりません" in result.stderr
    print("✓ 存在しないファイルのエラーハンドリングテスト成功")


def test_invalid_page_number():
    """無効なページ番号を指定した場合のエラーハンドリングを確認"""
    # まず、テスト用の簡単なPDFを作成
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        test_pdf_path = Path(__file__).parent / "test_temp.pdf"
        c = canvas.Canvas(str(test_pdf_path), pagesize=A4)
        c.drawString(100, 750, "Test Page 1")
        c.showPage()
        c.save()
        
        # ページ0を指定（無効）
        result = subprocess.run(
            ["python", "pdf_page_text.py", "--pdf", str(test_pdf_path), "--page", "0"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "ページ番号は1以上である必要があります" in result.stderr
        
        # 範囲外のページを指定
        result = subprocess.run(
            ["python", "pdf_page_text.py", "--pdf", str(test_pdf_path), "--page", "999"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "ページ番号が範囲外です" in result.stderr
        
        # クリーンアップ
        test_pdf_path.unlink()
        
        print("✓ 無効なページ番号のエラーハンドリングテスト成功")
        
    except ImportError:
        print("⚠ reportlab がインストールされていないため、一部のテストをスキップしました")


if __name__ == "__main__":
    print("=== pdf_page_text.py スモークテスト ===\n")
    
    try:
        test_help_option()
        test_missing_pdf_file()
        test_invalid_page_number()
        
        print("\n=== すべてのテストが成功しました ===")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ テスト失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ テスト実行エラー: {e}")
        sys.exit(1)

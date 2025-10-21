#!/usr/bin/env python3
"""
OCR機能のテスト

画像PDFからのOCRテキスト抽出機能を検証
"""

import sys
import subprocess
from pathlib import Path
import tempfile

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_text_pdf_with_japanese(pdf_path: Path) -> str:
    """日本語テキスト付きPDFを作成し、元のテキストを返す"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        
        # 日本語フォントを登録
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        
        test_text = "これはテストです"
        
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        c.setFont('HeiseiMin-W3', 24)  # 大きいフォントサイズでOCRしやすくする
        c.drawString(100, 750, test_text)
        c.showPage()
        c.save()
        
        return test_text
        
    except ImportError:
        raise ImportError("reportlab がインストールされていません")


def test_ocr_on_image_pdf():
    """
    画像PDFからOCRでテキストを抽出できることをテスト
    1. テキストPDFを作成
    2. PDFを画像PDFに変換
    3. OCRエンジンで画像PDFからテキストを抽出
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 1. 日本語テキストPDFを作成
            original_pdf = tmpdir_path / "original.pdf"
            expected_text = create_text_pdf_with_japanese(original_pdf)
            print(f"✓ テストPDFを作成: {original_pdf}")
            print(f"  期待されるテキスト: '{expected_text}'")
            
            # 2. PDFを画像PDFに変換
            images_dir = tmpdir_path / "images"
            image_pdf = tmpdir_path / "image_based.pdf"
            
            result = subprocess.run(
                ["python", "pdf_to_image.py",
                 "--pdf", str(original_pdf),
                 "--output-dir", str(images_dir),
                 "--create-pdf",
                 "--output-pdf", str(image_pdf),
                 "--dpi", "300"],  # 高解像度でOCRの精度を向上
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"画像変換失敗: {result.stderr}"
            assert image_pdf.exists(), "画像PDFが作成されませんでした"
            print(f"✓ 画像PDFを作成: {image_pdf}")
            
            # 3. 画像PDFからOCRでテキストを抽出（--engine ocr を明示的に指定）
            image_text_file = tmpdir_path / "image_based-1.txt"
            result = subprocess.run(
                ["python", str(Path(__file__).parent.parent / "pdf_page_text.py"),
                 "--pdf", str(image_pdf),
                 "--page", "1",
                 "--engine", "ocr"],
                cwd=tmpdir_path,
                capture_output=True,
                text=True
            )
            
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            
            assert result.returncode == 0, f"OCR抽出失敗: {result.stderr}"
            assert image_text_file.exists(), "OCRテキストファイルが作成されませんでした"
            
            with open(image_text_file, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            print(f"✓ OCRで抽出されたテキスト: '{ocr_text.strip()}'")
            
            # OCRでテキストが抽出できたことを確認
            # 注: OCRは完璧ではないため、元のテキストと完全一致しない可能性がある
            assert ocr_text.strip(), "OCRでテキストが抽出されませんでした"
            
            # 日本語文字が含まれていることを確認
            assert any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' 
                      for c in ocr_text), "日本語文字が検出されませんでした"
            
            print(f"✓ OCRテスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


def test_auto_fallback_to_ocr():
    """
    テキスト層がない場合に自動的にOCRにフォールバックすることをテスト
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 1. テキストPDFを作成
            original_pdf = tmpdir_path / "original.pdf"
            expected_text = create_text_pdf_with_japanese(original_pdf)
            print(f"✓ テストPDFを作成: {original_pdf}")
            
            # 2. PDFを画像PDFに変換
            images_dir = tmpdir_path / "images"
            image_pdf = tmpdir_path / "image_based.pdf"
            
            result = subprocess.run(
                ["python", "pdf_to_image.py",
                 "--pdf", str(original_pdf),
                 "--output-dir", str(images_dir),
                 "--create-pdf",
                 "--output-pdf", str(image_pdf),
                 "--dpi", "300"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"画像変換失敗: {result.stderr}"
            print(f"✓ 画像PDFを作成: {image_pdf}")
            
            # 3. 画像PDFからテキスト抽出（エンジン指定なし = pypdfがOCRにフォールバック）
            image_text_file = tmpdir_path / "image_based-1.txt"
            result = subprocess.run(
                ["python", str(Path(__file__).parent.parent / "pdf_page_text.py"),
                 "--pdf", str(image_pdf),
                 "--page", "1"],  # --engine 指定なし
                cwd=tmpdir_path,
                capture_output=True,
                text=True
            )
            
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            
            assert result.returncode == 0, f"テキスト抽出失敗: {result.stderr}"
            
            # OCRへのフォールバックメッセージが含まれていることを確認
            assert "OCRによる抽出を試みます" in result.stdout or "OCRでテキストを抽出しました" in result.stdout, \
                "OCRへのフォールバックが実行されませんでした"
            
            with open(image_text_file, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            print(f"✓ 自動フォールバックで抽出されたテキスト: '{ocr_text.strip()}'")
            
            # テキストが抽出できたことを確認
            assert ocr_text.strip(), "自動フォールバックでテキストが抽出されませんでした"
            
            print(f"✓ 自動フォールバックテスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


if __name__ == "__main__":
    print("=== OCR機能テスト ===\n")
    
    try:
        test_ocr_on_image_pdf()
        print()
        test_auto_fallback_to_ocr()
        
        print("\n=== すべてのOCRテストが成功しました ===")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ テスト失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
pdf_to_image.py のテスト

PDF画像変換機能のテストを実施
"""

import sys
import subprocess
from pathlib import Path
import tempfile
import shutil

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_test_pdf(pdf_path: Path) -> None:
    """テスト用の簡単なPDFを作成"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        
        # ページ1
        c.drawString(100, 750, "Test Page 1")
        c.drawString(100, 700, "これはテストページ1です")
        c.showPage()
        
        # ページ2
        c.drawString(100, 750, "Test Page 2")
        c.drawString(100, 700, "これはテストページ2です")
        c.showPage()
        
        # ページ3
        c.drawString(100, 750, "Test Page 3")
        c.drawString(100, 700, "これはテストページ3です")
        c.showPage()
        
        c.save()
        
    except ImportError:
        raise ImportError("reportlab がインストールされていません")


def test_help_option():
    """ヘルプオプションが正常に動作することを確認"""
    result = subprocess.run(
        ["python", "pdf_to_image.py", "--help"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "PDFファイルの各ページを画像に変換" in result.stdout
    print("✓ ヘルプオプションのテスト成功")


def test_missing_pdf_file():
    """存在しないPDFファイルを指定した場合のエラーハンドリングを確認"""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["python", "pdf_to_image.py", "--pdf", "nonexistent.pdf", "--output-dir", tmpdir],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "PDFファイルが見つかりません" in result.stderr
        print("✓ 存在しないファイルのエラーハンドリングテスト成功")


def test_convert_pdf_to_images():
    """PDFを画像に変換する基本機能をテスト"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用PDFを作成
            test_pdf_path = tmpdir_path / "test.pdf"
            create_test_pdf(test_pdf_path)
            
            # 出力ディレクトリ
            output_dir = tmpdir_path / "images"
            
            # PDF to 画像変換を実行
            result = subprocess.run(
                ["python", "pdf_to_image.py", 
                 "--pdf", str(test_pdf_path),
                 "--output-dir", str(output_dir)],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"変換失敗: {result.stderr}"
            
            # 画像ファイルが作成されたか確認
            image_files = list(output_dir.glob("*.png"))
            assert len(image_files) == 3, f"期待される画像数: 3、実際: {len(image_files)}"
            
            # ファイル名の確認
            expected_names = ["test-page1.png", "test-page2.png", "test-page3.png"]
            for name in expected_names:
                assert (output_dir / name).exists(), f"画像ファイルが見つかりません: {name}"
            
            print("✓ PDF to 画像変換テスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


def test_convert_with_page_range():
    """ページ範囲を指定してPDFを画像に変換するテスト"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用PDFを作成
            test_pdf_path = tmpdir_path / "test.pdf"
            create_test_pdf(test_pdf_path)
            
            # 出力ディレクトリ
            output_dir = tmpdir_path / "images"
            
            # ページ2-3のみ変換
            result = subprocess.run(
                ["python", "pdf_to_image.py", 
                 "--pdf", str(test_pdf_path),
                 "--output-dir", str(output_dir),
                 "--pages", "2", "3"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"変換失敗: {result.stderr}"
            
            # 画像ファイルが2つ作成されたか確認
            image_files = list(output_dir.glob("*.png"))
            assert len(image_files) == 2, f"期待される画像数: 2、実際: {len(image_files)}"
            
            # ファイル名の確認（ページ2と3のみ）
            assert (output_dir / "test-page2.png").exists()
            assert (output_dir / "test-page3.png").exists()
            assert not (output_dir / "test-page1.png").exists()
            
            print("✓ ページ範囲指定テスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


def test_convert_to_jpeg():
    """JPEG形式での変換をテスト"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用PDFを作成
            test_pdf_path = tmpdir_path / "test.pdf"
            create_test_pdf(test_pdf_path)
            
            # 出力ディレクトリ
            output_dir = tmpdir_path / "images"
            
            # JPEG形式で変換
            result = subprocess.run(
                ["python", "pdf_to_image.py", 
                 "--pdf", str(test_pdf_path),
                 "--output-dir", str(output_dir),
                 "--format", "jpeg"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"変換失敗: {result.stderr}"
            
            # JPEG画像ファイルが作成されたか確認
            image_files = list(output_dir.glob("*.jpeg"))
            assert len(image_files) == 3, f"期待される画像数: 3、実際: {len(image_files)}"
            
            print("✓ JPEG形式変換テスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


def test_create_image_pdf():
    """画像をPDFに再変換する機能をテスト"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用PDFを作成
            test_pdf_path = tmpdir_path / "test.pdf"
            create_test_pdf(test_pdf_path)
            
            # 出力ディレクトリ
            output_dir = tmpdir_path / "images"
            
            # PDF to 画像 to PDFを実行
            result = subprocess.run(
                ["python", "pdf_to_image.py", 
                 "--pdf", str(test_pdf_path),
                 "--output-dir", str(output_dir),
                 "--create-pdf"],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"変換失敗: {result.stderr}"
            
            # 画像PDFが作成されたか確認
            output_pdf = output_dir / "test_images.pdf"
            assert output_pdf.exists(), "画像PDFが作成されませんでした"
            
            # 画像ファイルも作成されているか確認
            image_files = list(output_dir.glob("*.png"))
            assert len(image_files) == 3
            
            print("✓ 画像PDF作成テスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


def test_custom_output_pdf_name():
    """カスタム出力PDF名の指定をテスト"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用PDFを作成
            test_pdf_path = tmpdir_path / "test.pdf"
            create_test_pdf(test_pdf_path)
            
            # 出力ディレクトリ
            output_dir = tmpdir_path / "images"
            custom_pdf_path = tmpdir_path / "custom_output.pdf"
            
            # カスタム名でPDF作成
            result = subprocess.run(
                ["python", "pdf_to_image.py", 
                 "--pdf", str(test_pdf_path),
                 "--output-dir", str(output_dir),
                 "--create-pdf",
                 "--output-pdf", str(custom_pdf_path)],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"変換失敗: {result.stderr}"
            
            # カスタム名のPDFが作成されたか確認
            assert custom_pdf_path.exists(), "カスタム名のPDFが作成されませんでした"
            
            print("✓ カスタム出力PDF名テスト成功")
            
    except ImportError:
        print("⚠ reportlab がインストールされていないため、テストをスキップしました")


if __name__ == "__main__":
    print("=== pdf_to_image.py テスト ===\n")
    
    try:
        test_help_option()
        test_missing_pdf_file()
        test_convert_pdf_to_images()
        test_convert_with_page_range()
        test_convert_to_jpeg()
        test_create_image_pdf()
        test_custom_output_pdf_name()
        
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

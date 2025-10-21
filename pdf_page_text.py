#!/usr/bin/env python3
"""
PDF 指定ページテキスト抽出 CLI ツール

指定されたPDFファイルの特定ページからテキストを抽出し、
テキストファイルとして保存します。
"""

import argparse
import sys
import logging
import unicodedata
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf ライブラリがインストールされていません。", file=sys.stderr)
    print("pip install -r requirements.txt を実行してください。", file=sys.stderr)
    sys.exit(1)

# pdfminer.six は任意のエンジンとしてインポート
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    from pdfminer.layout import LAParams
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

# OCR関連のライブラリをインポート
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def setup_logging():
    """ロギング設定を初期化"""
    # INFO以上のログは標準出力へ
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    
    # ERRORログは標準エラー出力へ
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[stdout_handler, stderr_handler]
    )


def validate_pdf_file(pdf_path: Path) -> None:
    """
    PDFファイルの存在とアクセス可能性を検証
    
    Args:
        pdf_path: PDFファイルのパス
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        PermissionError: ファイルへのアクセス権限がない場合
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    if not pdf_path.is_file():
        raise ValueError(f"指定されたパスはファイルではありません: {pdf_path}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        logging.warning(f"ファイル拡張子が .pdf ではありません: {pdf_path}")


def extract_page_text_pypdf(pdf_path: Path, page_number: int) -> str:
    """
    pypdf を使用してPDFの指定ページからテキストを抽出
    
    Args:
        pdf_path: PDFファイルのパス
        page_number: ページ番号（1始まり）
        
    Returns:
        抽出されたテキスト（Unicode NFC正規化済み）
        
    Raises:
        ValueError: ページ番号が範囲外の場合
        Exception: PDF読み込みやテキスト抽出に失敗した場合
    """
    try:
        reader = PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        
        logging.info(f"PDF総ページ数: {total_pages}")
        
        # ページ番号の検証（1始まりから0始まりに変換）
        page_index = page_number - 1
        
        if page_index < 0 or page_index >= total_pages:
            raise ValueError(
                f"ページ番号が範囲外です: {page_number} "
                f"(有効範囲: 1-{total_pages})"
            )
        
        logging.info(f"{pdf_path} の {page_number} ページ目を解析中...")
        
        # テキスト抽出
        page = reader.pages[page_index]
        text = page.extract_text()
        
        if not text or not text.strip():
            logging.warning(f"ページ {page_number} にテキストが見つかりませんでした")
            return ""
        
        # Unicode NFC正規化を適用（アキュート記号などの結合文字を正規化）
        text = unicodedata.normalize('NFC', text)
        
        return text
        
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        logging.error(f"PDFの読み込みまたはテキスト抽出に失敗しました: {e}")
        raise


def extract_page_text_pdfminer(pdf_path: Path, page_number: int) -> str:
    """
    pdfminer.six を使用してPDFの指定ページからテキストを抽出
    
    Args:
        pdf_path: PDFファイルのパス
        page_number: ページ番号（1始まり）
        
    Returns:
        抽出されたテキスト（Unicode NFC正規化済み）
        
    Raises:
        ValueError: ページ番号が範囲外の場合
        ImportError: pdfminer.six がインストールされていない場合
        Exception: PDF読み込みやテキスト抽出に失敗した場合
    """
    if not PDFMINER_AVAILABLE:
        raise ImportError(
            "pdfminer.six がインストールされていません。\n"
            "pip install pdfminer.six を実行してインストールしてください。"
        )
    
    try:
        # LAParams でレイアウト解析パラメータを設定
        laparams = LAParams(
            detect_vertical=True,
            all_texts=True
        )
        
        # ページ番号の検証（pdfminer.sixは0始まり）
        page_index = page_number - 1
        
        if page_number < 1:
            raise ValueError(f"ページ番号は1以上である必要があります: {page_number}")
        
        logging.info(f"{pdf_path} の {page_number} ページ目を解析中...")
        
        # テキスト抽出（ページ指定）
        text = pdfminer_extract_text(
            str(pdf_path),
            page_numbers=[page_index],
            laparams=laparams
        )
        
        if not text or not text.strip():
            logging.warning(f"ページ {page_number} にテキストが見つかりませんでした")
            return ""
        
        # Unicode NFC正規化を適用
        text = unicodedata.normalize('NFC', text)
        
        return text
        
    except Exception as e:
        if isinstance(e, (ValueError, ImportError)):
            raise
        logging.error(f"PDFの読み込みまたはテキスト抽出に失敗しました: {e}")
        raise


def extract_page_text_ocr(pdf_path: Path, page_number: int, lang: str = 'jpn+eng') -> str:
    """
    OCR（pytesseract）を使用してPDFの指定ページからテキストを抽出
    
    画像形式のPDF（テキスト層を持たないPDF）からテキストを抽出する際に使用します。
    
    Args:
        pdf_path: PDFファイルのパス
        page_number: ページ番号（1始まり）
        lang: OCRで使用する言語（デフォルト: 'jpn+eng'）
        
    Returns:
        抽出されたテキスト（Unicode NFC正規化済み）
        
    Raises:
        ValueError: ページ番号が範囲外の場合
        ImportError: PyMuPDF または pytesseract がインストールされていない場合
        Exception: PDF読み込みやOCR処理に失敗した場合
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError(
            "PyMuPDF (fitz) がインストールされていません。\n"
            "pip install PyMuPDF を実行してインストールしてください。"
        )
    
    if not PYTESSERACT_AVAILABLE:
        raise ImportError(
            "pytesseract がインストールされていません。\n"
            "pip install pytesseract を実行してインストールしてください。\n"
            "また、Tesseractエンジンのインストールも必要です。詳細はREADMEを参照してください。"
        )
    
    try:
        # PDFを開く
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        # ページ番号の検証（1始まりから0始まりに変換）
        page_index = page_number - 1
        
        if page_index < 0 or page_index >= total_pages:
            doc.close()
            raise ValueError(
                f"ページ番号が範囲外です: {page_number} "
                f"(有効範囲: 1-{total_pages})"
            )
        
        logging.info(f"{pdf_path} の {page_number} ページ目をOCRで解析中...")
        logging.info(f"使用言語: {lang}")
        
        # ページを取得
        page = doc[page_index]
        
        # ページを画像（pixmap）に変換（150 DPIでレンダリング）
        zoom = 150 / 72.0  # 150 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # pixmapをPIL Imageに変換
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # OCRでテキスト抽出
        text = pytesseract.image_to_string(img, lang=lang)
        
        # リソースを解放
        doc.close()
        
        if not text or not text.strip():
            logging.warning(f"ページ {page_number} からOCRでテキストを抽出できませんでした")
            return ""
        
        # Unicode NFC正規化を適用
        text = unicodedata.normalize('NFC', text)
        
        logging.info(f"OCRで {len(text)} 文字のテキストを抽出しました")
        
        return text
        
    except Exception as e:
        if isinstance(e, (ValueError, ImportError)):
            raise
        logging.error(f"OCR処理に失敗しました: {e}")
        raise


def extract_page_text(pdf_path: Path, page_number: int, engine: str = 'pypdf') -> str:
    """
    PDFの指定ページからテキストを抽出（エンジン選択可能）
    
    テキスト層が検出できない場合、自動的にOCRにフォールバックします。
    
    Args:
        pdf_path: PDFファイルのパス
        page_number: ページ番号（1始まり）
        engine: 抽出エンジン ('pypdf', 'pdfminer', または 'ocr')
        
    Returns:
        抽出されたテキスト（Unicode NFC正規化済み）
        
    Raises:
        ValueError: ページ番号が範囲外の場合、または無効なエンジン指定
        Exception: PDF読み込みやテキスト抽出に失敗した場合
    """
    # OCRエンジンが明示的に指定された場合
    if engine == 'ocr':
        return extract_page_text_ocr(pdf_path, page_number)
    
    # pypdf または pdfminer でテキスト抽出を試みる
    if engine == 'pypdf':
        text = extract_page_text_pypdf(pdf_path, page_number)
    elif engine == 'pdfminer':
        text = extract_page_text_pdfminer(pdf_path, page_number)
    else:
        raise ValueError(
            f"無効な抽出エンジンです: {engine}\n"
            f"有効なエンジン: 'pypdf', 'pdfminer', 'ocr'"
        )
    
    # テキストが空の場合、OCRにフォールバック
    if not text or not text.strip():
        if PYMUPDF_AVAILABLE and PYTESSERACT_AVAILABLE:
            logging.info("テキスト層が見つかりませんでした。OCRによる抽出を試みます...")
            try:
                text = extract_page_text_ocr(pdf_path, page_number)
                if text and text.strip():
                    logging.info("OCRでテキストを抽出しました")
                else:
                    logging.warning("OCRでもテキストを抽出できませんでした")
            except Exception as e:
                logging.warning(f"OCR処理に失敗しました: {e}")
                # OCRが失敗した場合は、元の空のテキストを返す
                text = ""
        else:
            missing_deps = []
            if not PYMUPDF_AVAILABLE:
                missing_deps.append("PyMuPDF")
            if not PYTESSERACT_AVAILABLE:
                missing_deps.append("pytesseract")
            
            logging.warning(
                f"テキスト層が見つかりませんでしたが、OCR機能が利用できません。\n"
                f"OCR機能を使用するには、以下のライブラリをインストールしてください: {', '.join(missing_deps)}"
            )
    
    return text


def generate_output_filename(pdf_path: Path, page_number: int) -> Path:
    """
    出力ファイル名を生成
    
    Args:
        pdf_path: 元のPDFファイルのパス
        page_number: ページ番号
        
    Returns:
        出力ファイルのパス
    """
    # 拡張子を除いたベース名を取得
    base_name = pdf_path.stem
    output_filename = f"{base_name}-{page_number}.txt"
    
    # 実行場所（カレントディレクトリ）に出力
    output_path = Path.cwd() / output_filename
    
    return output_path


def save_text_to_file(text: str, output_path: Path) -> None:
    """
    テキストをファイルに保存
    
    Args:
        text: 保存するテキスト
        output_path: 出力ファイルのパス
        
    Raises:
        IOError: ファイルへの書き込みに失敗した場合
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logging.info(f"出力ファイル: {output_path}")
    except Exception as e:
        logging.error(f"ファイルへの書き込みに失敗しました: {e}")
        raise


def parse_arguments() -> argparse.Namespace:
    """
    コマンドライン引数を解析
    
    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(
        description='PDFファイルの指定ページからテキストを抽出します。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s --pdf ./sample.pdf --page 3
  %(prog)s --pdf document.pdf --page 1
  %(prog)s --pdf accented.pdf --page 1 --engine pdfminer
        """
    )
    
    parser.add_argument(
        '--pdf',
        type=str,
        required=True,
        help='PDFファイルのパス',
        metavar='<PDFファイルパス>'
    )
    
    parser.add_argument(
        '--page',
        type=int,
        required=True,
        help='抽出するページ番号（1始まり）',
        metavar='<ページ番号>'
    )
    
    parser.add_argument(
        '--engine',
        type=str,
        choices=['pypdf', 'pdfminer', 'ocr'],
        default='pypdf',
        help='テキスト抽出エンジン（デフォルト: pypdf）。文字化けが発生する場合は pdfminer を試してください。画像PDFの場合は ocr を使用してください。',
        metavar='<エンジン>'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    メイン処理
    
    Returns:
        終了コード（0: 成功、非0: エラー）
    """
    setup_logging()
    
    try:
        # 引数解析
        args = parse_arguments()
        
        logging.info("テキスト抽出を開始します...")
        
        # PDFファイルパスの処理
        pdf_path = Path(args.pdf).resolve()
        page_number = args.page
        engine = args.engine
        
        # エンジンの利用可能性チェック
        if engine == 'pdfminer' and not PDFMINER_AVAILABLE:
            logging.error(
                "pdfminer エンジンが選択されましたが、pdfminer.six がインストールされていません。\n"
                "pip install pdfminer.six を実行してインストールするか、\n"
                "デフォルトの pypdf エンジンを使用してください（--engine pypdf または引数省略）。"
            )
            return 1
        
        logging.info(f"使用する抽出エンジン: {engine}")
        
        # ページ番号の基本検証
        if page_number < 1:
            logging.error(f"ページ番号は1以上である必要があります: {page_number}")
            return 1
        
        # PDFファイルの検証
        validate_pdf_file(pdf_path)
        
        # テキスト抽出
        text = extract_page_text(pdf_path, page_number, engine)
        
        # 出力ファイル名生成
        output_path = generate_output_filename(pdf_path, page_number)
        
        # ファイルに保存
        save_text_to_file(text, output_path)
        
        logging.info("正常終了")
        return 0
        
    except FileNotFoundError as e:
        logging.error(str(e))
        return 1
        
    except ValueError as e:
        logging.error(str(e))
        return 1
        
    except PermissionError as e:
        logging.error(f"ファイルへのアクセス権限がありません: {e}")
        return 1
    
    except ImportError as e:
        logging.error(str(e))
        return 1
        
    except KeyboardInterrupt:
        logging.error("\n処理が中断されました")
        return 130
        
    except Exception as e:
        logging.error(f"予期しないエラーが発生しました: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

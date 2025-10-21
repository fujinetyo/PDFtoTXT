#!/usr/bin/env python3
"""
PDF ページを画像に変換する CLI ツール

指定されたPDFファイルの各ページを画像（PNG/JPEG）に変換し、
オプションで画像を再びPDFに結合する機能を提供します。
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF ライブラリがインストールされていません。", file=sys.stderr)
    print("pip install PyMuPDF を実行してください。", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow ライブラリがインストールされていません。", file=sys.stderr)
    print("pip install Pillow を実行してください。", file=sys.stderr)
    sys.exit(1)


def setup_logging():
    """ロギング設定を初期化"""
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    
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
        ValueError: ファイルではない場合
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    if not pdf_path.is_file():
        raise ValueError(f"指定されたパスはファイルではありません: {pdf_path}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        logging.warning(f"ファイル拡張子が .pdf ではありません: {pdf_path}")


def convert_pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    image_format: str = 'png',
    dpi: int = 150,
    page_range: Optional[tuple] = None
) -> List[Path]:
    """
    PDFの各ページを画像ファイルに変換
    
    Args:
        pdf_path: PDFファイルのパス
        output_dir: 出力ディレクトリのパス
        image_format: 画像フォーマット ('png' または 'jpeg')
        dpi: 解像度（DPI）
        page_range: ページ範囲のタプル (開始, 終了)。Noneの場合は全ページ
        
    Returns:
        変換された画像ファイルのパスのリスト
        
    Raises:
        Exception: PDF読み込みや画像変換に失敗した場合
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        logging.info(f"PDF総ページ数: {total_pages}")
        
        # ページ範囲の決定
        if page_range:
            start_page, end_page = page_range
            start_page = max(0, start_page - 1)  # 1始まりから0始まりに変換
            end_page = min(total_pages, end_page)
        else:
            start_page = 0
            end_page = total_pages
        
        logging.info(f"変換範囲: ページ {start_page + 1} から {end_page}")
        
        # 各ページを画像に変換
        for page_num in range(start_page, end_page):
            page = doc[page_num]
            
            # 解像度の設定（dpi/72でズーム倍率を計算）
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # ページを画像（pixmap）にレンダリング
            pix = page.get_pixmap(matrix=mat)
            
            # 出力ファイル名を生成
            base_name = pdf_path.stem
            output_filename = f"{base_name}-page{page_num + 1}.{image_format}"
            output_path = output_dir / output_filename
            
            # 画像を保存
            if image_format.lower() == 'png':
                pix.save(str(output_path))
            elif image_format.lower() in ['jpg', 'jpeg']:
                # JPEGの場合、Pillowを使用してRGBモードで保存
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(str(output_path), "JPEG", quality=95)
            
            image_paths.append(output_path)
            logging.info(f"ページ {page_num + 1} を保存: {output_path}")
        
        doc.close()
        logging.info(f"合計 {len(image_paths)} ページを変換しました")
        
        return image_paths
        
    except Exception as e:
        logging.error(f"PDF画像変換に失敗しました: {e}")
        raise


def images_to_pdf(image_paths: List[Path], output_pdf_path: Path) -> None:
    """
    画像ファイルを1つのPDFファイルに結合
    
    Args:
        image_paths: 画像ファイルパスのリスト
        output_pdf_path: 出力PDFファイルのパス
        
    Raises:
        Exception: PDF作成に失敗した場合
    """
    try:
        if not image_paths:
            raise ValueError("画像ファイルのリストが空です")
        
        logging.info(f"{len(image_paths)} 枚の画像をPDFに変換中...")
        
        # 最初の画像を開く
        images = []
        first_image = Image.open(str(image_paths[0]))
        
        # 残りの画像を開く
        for img_path in image_paths[1:]:
            img = Image.open(str(img_path))
            # RGBモードに変換（PDFはRGBが必要）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        # 最初の画像もRGBモードに変換
        if first_image.mode != 'RGB':
            first_image = first_image.convert('RGB')
        
        # PDFとして保存
        first_image.save(
            str(output_pdf_path),
            "PDF",
            save_all=True,
            append_images=images,
            resolution=150.0
        )
        
        # 画像を閉じる
        first_image.close()
        for img in images:
            img.close()
        
        logging.info(f"画像PDFを作成しました: {output_pdf_path}")
        
    except Exception as e:
        logging.error(f"画像からPDF作成に失敗しました: {e}")
        raise


def parse_arguments() -> argparse.Namespace:
    """
    コマンドライン引数を解析
    
    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(
        description='PDFファイルの各ページを画像に変換し、オプションで画像PDFに再変換します。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # PDFを画像に変換（PNG形式）
  %(prog)s --pdf sample.pdf --output-dir ./images

  # PDFを画像に変換し、画像PDFとして再結合
  %(prog)s --pdf sample.pdf --output-dir ./images --create-pdf

  # JPEG形式で保存、解像度300dpi
  %(prog)s --pdf sample.pdf --output-dir ./images --format jpeg --dpi 300

  # 特定のページ範囲のみ変換（3ページ目から5ページ目）
  %(prog)s --pdf sample.pdf --output-dir ./images --pages 3 5
        """
    )
    
    parser.add_argument(
        '--pdf',
        type=str,
        required=True,
        help='入力PDFファイルのパス',
        metavar='<PDFファイルパス>'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='画像ファイルの出力ディレクトリ',
        metavar='<出力ディレクトリ>'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['png', 'jpeg', 'jpg'],
        default='png',
        help='画像フォーマット（デフォルト: png）',
        metavar='<フォーマット>'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='画像の解像度（DPI）（デフォルト: 150）',
        metavar='<DPI>'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        nargs=2,
        help='変換するページ範囲（開始 終了）。指定しない場合は全ページ',
        metavar=('開始ページ', '終了ページ')
    )
    
    parser.add_argument(
        '--create-pdf',
        action='store_true',
        help='変換した画像を1つのPDFファイルに結合する'
    )
    
    parser.add_argument(
        '--output-pdf',
        type=str,
        help='結合PDFファイルの出力パス（--create-pdf と併用）',
        metavar='<出力PDFパス>'
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
        
        logging.info("PDF画像変換を開始します...")
        
        # パスの処理
        pdf_path = Path(args.pdf).resolve()
        output_dir = Path(args.output_dir).resolve()
        
        # PDFファイルの検証
        validate_pdf_file(pdf_path)
        
        # 画像フォーマットの正規化
        image_format = 'jpeg' if args.format in ['jpg', 'jpeg'] else 'png'
        
        # ページ範囲の処理
        page_range = None
        if args.pages:
            start_page, end_page = args.pages
            if start_page < 1:
                logging.error("開始ページは1以上である必要があります")
                return 1
            if end_page < start_page:
                logging.error("終了ページは開始ページ以上である必要があります")
                return 1
            page_range = (start_page, end_page)
        
        # DPI検証
        if args.dpi < 72 or args.dpi > 600:
            logging.warning(f"DPI値が推奨範囲外です: {args.dpi}（推奨: 72-600）")
        
        # PDFを画像に変換
        image_paths = convert_pdf_to_images(
            pdf_path,
            output_dir,
            image_format,
            args.dpi,
            page_range
        )
        
        # オプション: 画像をPDFに結合
        if args.create_pdf:
            if args.output_pdf:
                output_pdf_path = Path(args.output_pdf).resolve()
            else:
                # デフォルトの出力PDF名を生成
                output_pdf_path = output_dir / f"{pdf_path.stem}_images.pdf"
            
            images_to_pdf(image_paths, output_pdf_path)
        
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
        
    except KeyboardInterrupt:
        logging.error("\n処理が中断されました")
        return 130
        
    except Exception as e:
        logging.error(f"予期しないエラーが発生しました: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

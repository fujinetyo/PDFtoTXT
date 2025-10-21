# PDFtoTXT

PDFファイルの指定ページからテキストを抽出する CLI ツール

## 概要

このツールは、PDFファイルとページ番号を引数に取り、そのページに記載されているテキストを抽出してテキストファイルとして出力します。

## 機能

- 指定されたPDFファイルの特定ページからテキストを抽出
- 抽出したテキストを `<元PDF名>-<ページ番号>.txt` 形式で保存
- 日本語を含む実行結果のログ出力
- 詳細なエラーメッセージとエラーハンドリング
- **新機能**: 画像PDF（テキスト層なし）からOCRでテキストを自動抽出
- **新機能**: PDFページを画像に変換し、画像PDFとして再構成する機能

## 必要環境

- Python 3.10 以上（Python 3.12 で動作確認済み）
- pip（パッケージ管理ツール）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/fujinetyo/PDFtoTXT.git
cd PDFtoTXT
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv .venv
```

### 3. 仮想環境の有効化

**macOS / Linux の場合:**

```bash
source .venv/bin/activate
```

**Windows の場合:**

```bash
.venv\Scripts\activate
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 5. Tesseract OCRエンジンのインストール（画像PDFからテキストを抽出する場合）

画像形式のPDF（テキスト層を持たないPDF）からテキストを抽出する場合は、Tesseract OCRエンジンのインストールが必要です。

**macOS の場合:**

```bash
brew install tesseract
brew install tesseract-lang  # 日本語を含む追加言語パック
```

**Ubuntu / Debian の場合:**

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn
```

**Windows の場合:**

1. [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) から Windows版インストーラーをダウンロード
2. インストール時に「Additional language data」で「Japanese」を選択
3. インストール後、環境変数PATHにTesseractのインストールパスを追加

**インストール確認:**

```bash
tesseract --version
tesseract --list-langs  # jpn が表示されることを確認
```

## 使い方

### 基本的な使用方法

```bash
python pdf_page_text.py --pdf <PDFファイルパス> --page <ページ番号> [--engine <エンジン>]
```

### 抽出エンジンについて

このツールは3つのテキスト抽出エンジンをサポートしています：

1. **pypdf**（デフォルト）
   - 純Python実装で、外部依存が少ない
   - 高速で一般的なPDFに対応
   - 一部のPDFでアキュート記号付き文字やアポストロフィが正しく抽出できない場合がある
   - テキスト層がない場合は自動的にOCRにフォールバック

2. **pdfminer**（`pdfminer.six` パッケージ）
   - より高度なPDF解析機能
   - 複雑なフォントエンコーディングやレイアウトに対応
   - pypdfで文字化けが発生する場合の代替手段として推奨
   - テキスト層がない場合は自動的にOCRにフォールバック

3. **ocr**（Tesseract OCRエンジン）
   - 画像形式のPDF（テキスト層を持たないPDF）からテキストを抽出
   - 日本語と英語の両方に対応（jpn+eng）
   - Tesseract OCRエンジンのインストールが必要
   - pypdfやpdfminerでテキストが検出できない場合、自動的にOCRが実行されます

### エンジンの切り替え方法

文字化けが発生する場合は、`--engine pdfminer` オプションを使用してください：

```bash
python pdf_page_text.py --pdf ./document.pdf --page 1 --engine pdfminer
```

### 使用例

#### 例1: カレントディレクトリのPDFファイルから3ページ目を抽出

```bash
python pdf_page_text.py --pdf ./sample.pdf --page 3
```

**期待される出力:**

```
INFO: テキスト抽出を開始します...
INFO: PDF総ページ数: 10
INFO: /path/to/sample.pdf の 3 ページ目を解析中...
INFO: 出力ファイル: /path/to/current/dir/sample-3.txt
INFO: 正常終了
```

#### 例2: 別のディレクトリにあるPDFファイルから1ページ目を抽出

```bash
python pdf_page_text.py --pdf /path/to/documents/report.pdf --page 1
```

#### 例3: OCRエンジンを使用して画像PDFからテキストを抽出

```bash
python pdf_page_text.py --pdf ./scanned_document.pdf --page 1 --engine ocr
```

#### 例4: 自動OCRフォールバック（画像PDFの場合）

```bash
# テキスト層がない場合、自動的にOCRが実行されます
python pdf_page_text.py --pdf ./image_based.pdf --page 1
```

#### 例5: ヘルプの表示

```bash
python pdf_page_text.py --help
```

### 引数の説明

| 引数 | 必須 | 説明 |
|------|------|------|
| `--pdf <PDFファイルパス>` | ✓ | 抽出元のPDFファイルのパス（相対パスまたは絶対パス） |
| `--page <ページ番号>` | ✓ | 抽出するページ番号（1始まり） |
| `--engine <エンジン>` | | テキスト抽出エンジン（`pypdf`, `pdfminer`, または `ocr`）。デフォルトは `pypdf`。文字化けが発生する場合は `pdfminer` を試してください。画像PDFの場合は `ocr` を使用してください。テキスト層がない場合は自動的にOCRにフォールバックします。 |

## 出力

- **出力先:** 実行したカレントディレクトリ
- **ファイル名形式:** `<元のPDFファイル名>-<ページ番号>.txt`
  - 例: `sample.pdf` の 3 ページ目 → `sample-3.txt`
  - 例: `report.pdf` の 12 ページ目 → `report-12.txt`

## エラーハンドリング

このツールは以下のエラーを検出し、適切なメッセージを日本語で出力します：

### エラーの種類と対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `PDFファイルが見つかりません` | 指定されたファイルが存在しない | ファイルパスを確認してください |
| `ページ番号が範囲外です` | 指定されたページ番号がPDFの範囲外 | 1からPDFの総ページ数の範囲内で指定してください |
| `ファイルへのアクセス権限がありません` | ファイルの読み込み/書き込み権限がない | ファイルの権限を確認してください |
| `pypdf ライブラリがインストールされていません` | 依存ライブラリが未インストール | `pip install -r requirements.txt` を実行してください |

### エラー時の動作

- エラー発生時は非0の終了コードで終了します
- エラーメッセージは標準エラー出力に日本語で出力されます

## 制限事項

1. **レイアウトの保持:** テキストのレイアウト（段組み、表形式など）は保持されません
2. **暗号化されたPDF:** パスワード保護されたPDFには対応していません
3. **フォント:** 特殊なフォントや埋め込まれていないフォントの場合、正しく抽出できない可能性があります。その場合は代替エンジン（`--engine pdfminer`）を試してください。
4. **改行・空白:** 元のPDFの改行や空白は適宜変換されます
5. **OCR精度:** OCR機能は画像の品質、フォントサイズ、背景ノイズなどによって精度が変動します。より高い精度が必要な場合は、元のPDFを高解像度（300 DPI以上）でスキャンしてください。

### 文字エンコーディングに関する注意事項

- 出力ファイルは常に **UTF-8** でエンコードされます
- アキュート記号付き文字やアポストロフィは **Unicode NFC正規化** が適用され、環境依存の表示問題を最小限にします
- 一部のPDFでは、フォントのエンコーディング情報が不完全な場合があります。その場合は `--engine pdfminer` を試してください

## 依存ライブラリ

- **pypdf** (>=4.0.0): PDFファイルからのテキスト抽出（デフォルトエンジン）
- **pdfminer.six** (>=20231228): 代替テキスト抽出エンジン（オプション）
- **PyMuPDF** (>=1.24.0): PDF画像化機能用、OCR機能用
- **Pillow** (>=10.2.0): 画像処理・PDF生成用、OCR機能用
- **pytesseract** (>=0.3.10): OCR機能用（Python wrapper）
- **Tesseract OCR**: OCRエンジン本体（システムレベルでのインストールが必要）

詳細は `requirements.txt` を参照してください。

### pdfminer.six のインストール

`pdfminer.six` エンジンを使用する場合は、以下のコマンドでインストールしてください：

```bash
pip install pdfminer.six
```

または、`requirements.txt` から一括インストール：

```bash
pip install -r requirements.txt
```

### Tesseract OCRのインストール

OCR機能を使用する場合は、Tesseract OCRエンジンのインストールが必要です。詳細は「セットアップ」セクションの「5. Tesseract OCRエンジンのインストール」を参照してください。

## 動作確認環境

- macOS（推奨）
- Linux（推奨）
- Windows（基本的に動作するはずですが、パスの扱いに注意が必要）

## トラブルシューティング

### 文字化けが発生する場合

アキュート記号付き文字（é、ñ、ö など）やアポストロフィ（'、' など）が正しく表示されない場合：

1. **代替エンジンを試す**
   ```bash
   python pdf_page_text.py --pdf ./document.pdf --page 1 --engine pdfminer
   ```

2. **ロケール設定を確認**
   
   システムのロケールがUTF-8に設定されているか確認してください：
   
   ```bash
   # macOS / Linux
   locale
   # LANG=ja_JP.UTF-8 または en_US.UTF-8 などが表示されることを確認
   ```
   
   もしUTF-8ロケールが設定されていない場合：
   
   ```bash
   # 一時的に設定
   export LANG=ja_JP.UTF-8
   export LC_ALL=ja_JP.UTF-8
   
   # または環境変数 PYTHONIOENCODING を設定
   export PYTHONIOENCODING=utf-8
   ```

3. **出力ファイルの確認**
   
   出力ファイルは常にUTF-8でエンコードされます。テキストエディタでファイルを開く際は、UTF-8エンコーディングを指定してください。

### OCRが動作しない場合

画像PDFからテキストを抽出できない場合：

1. **Tesseractがインストールされているか確認**
   
   ```bash
   tesseract --version
   tesseract --list-langs  # jpn が表示されることを確認
   ```
   
   インストールされていない場合は、「セットアップ」セクションの手順に従ってインストールしてください。

2. **日本語言語パックがインストールされているか確認**
   
   `tesseract --list-langs` の出力に `jpn` が含まれていることを確認してください。
   含まれていない場合は、日本語言語パックをインストールしてください：
   
   ```bash
   # Ubuntu / Debian
   sudo apt-get install tesseract-ocr-jpn
   
   # macOS
   brew install tesseract-lang
   ```

3. **PDF画像の品質を確認**
   
   OCRの精度は元の画像の品質に大きく依存します。以下を確認してください：
   
   - 解像度が十分高いか（推奨: 300 DPI以上）
   - 文字が明瞭に読めるか
   - 背景ノイズが少ないか
   - 文字サイズが適切か（小さすぎないか）

4. **手動でOCRエンジンを指定**
   
   ```bash
   python pdf_page_text.py --pdf ./image.pdf --page 1 --engine ocr
   ```

5. **エラーメッセージを確認**
   
   詳細なエラーメッセージが表示される場合は、そのメッセージに従って問題を解決してください。

### pypdf がインストールできない

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 仮想環境が有効化されない

仮想環境のパスが正しいか確認してください。また、Pythonのバージョンが3.10以上であることを確認してください。

```bash
python --version
```

### 出力ファイルが見つからない

出力ファイルはツールを実行したカレントディレクトリに作成されます。実行時のカレントディレクトリを確認してください。

```bash
pwd  # カレントディレクトリを表示
ls -la *.txt  # 生成されたテキストファイルを確認
```

## ライセンス

このプロジェクトのライセンスについては、リポジトリのライセンスファイルを参照してください。

## テスト

基本的なスモークテストが `tests/` ディレクトリに含まれています。

```bash
# テストの実行
python tests/test_smoke.py           # pdf_page_text.py のテスト
python tests/test_pdf_to_image.py    # pdf_to_image.py のテスト
python tests/test_integration.py     # 統合テスト
python tests/test_ocr.py             # OCR機能のテスト
```

テストを実行するには、`reportlab` ライブラリが必要です（テスト用PDFの生成に使用）:

```bash
pip install reportlab
```

OCRテストを実行するには、さらにTesseract OCRエンジンのインストールが必要です。詳細は「セットアップ」セクションを参照してください。

## PDF画像化機能（新機能）

`pdf_to_image.py` を使用して、PDFファイルの各ページを画像に変換できます。この機能は、OCRテストやテキスト抽出精度の評価に役立ちます。

### 基本的な使用方法

```bash
python pdf_to_image.py --pdf <PDFファイルパス> --output-dir <出力ディレクトリ> [オプション]
```

### 使用例

#### 例1: PDFを画像に変換（PNG形式）

```bash
python pdf_to_image.py --pdf sample.pdf --output-dir ./images
```

各ページが `sample-page1.png`, `sample-page2.png`, ... として保存されます。

#### 例2: PDFを画像に変換し、画像PDFとして再結合

```bash
python pdf_to_image.py --pdf sample.pdf --output-dir ./images --create-pdf
```

画像ファイルを作成後、それらを1つのPDF（`sample_images.pdf`）にまとめます。

#### 例3: JPEG形式で保存、高解像度（300dpi）

```bash
python pdf_to_image.py --pdf sample.pdf --output-dir ./images --format jpeg --dpi 300
```

#### 例4: 特定のページ範囲のみ変換

```bash
# 3ページ目から5ページ目まで変換
python pdf_to_image.py --pdf sample.pdf --output-dir ./images --pages 3 5
```

#### 例5: カスタムPDF名で画像PDFを作成

```bash
python pdf_to_image.py --pdf sample.pdf --output-dir ./images --create-pdf --output-pdf ./output.pdf
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--pdf <PDFファイルパス>` | 入力PDFファイルのパス（必須） | - |
| `--output-dir <出力ディレクトリ>` | 画像ファイルの出力ディレクトリ（必須） | - |
| `--format <フォーマット>` | 画像フォーマット（png, jpeg, jpg） | png |
| `--dpi <DPI>` | 画像の解像度（72-600推奨） | 150 |
| `--pages <開始> <終了>` | 変換するページ範囲 | 全ページ |
| `--create-pdf` | 変換した画像を1つのPDFに結合 | 無効 |
| `--output-pdf <出力PDFパス>` | 結合PDFの出力パス（--create-pdfと併用） | `<元PDF名>_images.pdf` |

### テキスト抽出精度の比較

画像化機能を使用して、テキストPDFと画像PDFのテキスト抽出結果を比較できます：

```bash
# 1. 元のテキストPDFからテキストを抽出
python pdf_page_text.py --pdf original.pdf --page 1

# 2. PDFを画像化して画像PDFを作成
python pdf_to_image.py --pdf original.pdf --output-dir ./images --create-pdf --output-pdf image_based.pdf

# 3. 画像PDFからテキストを抽出（空または限定的な結果）
python pdf_page_text.py --pdf image_based.pdf --page 1

# 4. 2つのテキストファイルを比較
diff original-1.txt image_based-1.txt
```

画像PDFからはテキストレイヤーが除去されるため、テキスト抽出結果は空または限定的になります。これにより、OCR機能のテストやテキスト抽出精度の評価が可能になります。

## 貢献

バグ報告や機能リクエストは GitHub の Issues でお願いします。

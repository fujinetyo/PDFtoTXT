# PDFtoTXT

PDFファイルの指定ページからテキストを抽出する CLI ツール

## 概要

このツールは、PDFファイルとページ番号を引数に取り、そのページに記載されているテキストを抽出してテキストファイルとして出力します。

## 機能

- 指定されたPDFファイルの特定ページからテキストを抽出
- 抽出したテキストを `<元PDF名>-<ページ番号>.txt` 形式で保存
- 日本語を含む実行結果のログ出力
- 詳細なエラーメッセージとエラーハンドリング

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

## 使い方

### 基本的な使用方法

```bash
python pdf_page_text.py --pdf <PDFファイルパス> --page <ページ番号> [--engine <エンジン>]
```

### 抽出エンジンについて

このツールは2つのテキスト抽出エンジンをサポートしています：

1. **pypdf**（デフォルト）
   - 純Python実装で、外部依存が少ない
   - 高速で一般的なPDFに対応
   - 一部のPDFでアキュート記号付き文字やアポストロフィが正しく抽出できない場合がある

2. **pdfminer**（`pdfminer.six` パッケージ）
   - より高度なPDF解析機能
   - 複雑なフォントエンコーディングやレイアウトに対応
   - pypdfで文字化けが発生する場合の代替手段として推奨

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

#### 例3: pdfminer エンジンを使用してテキストを抽出

```bash
python pdf_page_text.py --pdf ./accented.pdf --page 1 --engine pdfminer
```

#### 例4: ヘルプの表示

```bash
python pdf_page_text.py --help
```

### 引数の説明

| 引数 | 必須 | 説明 |
|------|------|------|
| `--pdf <PDFファイルパス>` | ✓ | 抽出元のPDFファイルのパス（相対パスまたは絶対パス） |
| `--page <ページ番号>` | ✓ | 抽出するページ番号（1始まり） |
| `--engine <エンジン>` | | テキスト抽出エンジン（`pypdf` または `pdfminer`）。デフォルトは `pypdf`。文字化けが発生する場合は `pdfminer` を試してください。 |

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
2. **画像内のテキスト:** 画像として埋め込まれたテキスト（OCRが必要なもの）は抽出できません
3. **暗号化されたPDF:** パスワード保護されたPDFには対応していません
4. **フォント:** 特殊なフォントや埋め込まれていないフォントの場合、正しく抽出できない可能性があります。その場合は代替エンジン（`--engine pdfminer`）を試してください。
5. **改行・空白:** 元のPDFの改行や空白は適宜変換されます

### 文字エンコーディングに関する注意事項

- 出力ファイルは常に **UTF-8** でエンコードされます
- アキュート記号付き文字やアポストロフィは **Unicode NFC正規化** が適用され、環境依存の表示問題を最小限にします
- 一部のPDFでは、フォントのエンコーディング情報が不完全な場合があります。その場合は `--engine pdfminer` を試してください

## 依存ライブラリ

- **pypdf** (>=4.0.0): PDFファイルからのテキスト抽出（デフォルトエンジン）
- **pdfminer.six** (>=20231228): 代替テキスト抽出エンジン（オプション）

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
python tests/test_smoke.py
```

テストを実行するには、`reportlab` ライブラリが必要です（テスト用PDFの生成に使用）:

```bash
pip install reportlab
```

## 貢献

バグ報告や機能リクエストは GitHub の Issues でお願いします。

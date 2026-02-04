# charenc 仕様書

## 概要

AIエージェントで cp932 等の非UTF-8ファイルを編集する際の文字化け問題を解決するスキル。

**ワークフロー**: `cp932ファイル → UTF-8に変換 → 編集 → cp932に戻す`

## スクリプト仕様

### convert_to_utf8.py

指定されたエンコーディングのファイルをUTF-8に変換する。

**機能**:
- 指定されたエンコーディングのファイルをUTF-8に変換
- バックアップファイル（`.{encoding}.bak`）を自動作成
- メタデータファイル（`.charenc_meta/{filename}.json`）に元情報を保存

**使用方法**:
```bash
python convert_to_utf8.py <file> --encoding <encoding>
```

**オプション**:
| オプション | 説明 | 必須 |
|-----------|------|------|
| `--encoding`, `-e` | 元のエンコーディング | Yes |
| `--output`, `-o` | 出力先（デフォルト: 上書き） | No |
| `--backup-dir` | バックアップ保存先 | No |
| `--no-backup` | バックアップを作成しない | No |

**メタデータ形式**:
```json
{
  "original_file": "example.txt",
  "output_file": "example.txt",
  "original_encoding": "cp932",
  "original_size": 1024,
  "original_hash": "sha256hash...",
  "converted_hash": "sha256hash...",
  "backup_path": "example.txt.cp932.bak",
  "line_ending": "CRLF",
  "converted_at": "2026-02-03T10:30:00"
}
```

### restore_encoding.py

UTF-8ファイルをメタデータに基づいて元のエンコーディングに復元する。

**機能**:
- UTF-8ファイルをメタデータに基づいて元のエンコーディングに復元
- 改行コード（CRLF/LF）も復元
- バックアップとメタデータをクリーンアップ

**使用方法**:
```bash
python restore_encoding.py <file>
```

**オプション**:
| オプション | 説明 |
|-----------|------|
| `--encoding`, `-e` | 復元先エンコーディング（メタデータより優先） |
| `--output`, `-o` | 出力先（デフォルト: 上書き） |
| `--errors` | エラー処理: strict/replace/backslashreplace/xmlcharrefreplace |
| `--keep-backup` | バックアップを保持 |
| `--strict-hash` | ハッシュ不一致をエラーにする（`--force`で上書き） |
| `--force`, `-f` | ハッシュ不一致でも強制的に続行（主に`--strict-hash`用） |

**ハッシュ検証**:
- デフォルト: ハッシュ不一致でも警告して続行
- `--strict-hash`: ハッシュ不一致でエラー（`--force`で続行可能）

**エラー処理オプション**:
- `strict`: 変換不可能な文字でエラー（デフォルト）
- `replace`: `?` に置換
- `backslashreplace`: `\xNN` 形式で表示
- `xmlcharrefreplace`: `&#NNN;` 形式で表示

## サポートするエンコーディング

### 日本語
| エンコーディング | 用途 |
|----------------|------|
| cp932 | Windows日本語（Shift-JIS拡張） |
| shift_jis | 標準Shift-JIS |
| euc-jp | Unix日本語 |
| iso-2022-jp | JISメール |
| euc-jis-2004 | JIS X 0213 |

### Unicode
| エンコーディング | 用途 |
|----------------|------|
| utf-8 | Unicode（標準） |
| utf-8-sig | UTF-8 with BOM |
| utf-16 | UTF-16 with BOM |
| utf-16-le/be | UTF-16 Little/Big Endian |

### Western
| エンコーディング | 用途 |
|----------------|------|
| latin-1 | Western European |
| cp1252 | Windows Western |
| ascii | 7-bit ASCII |

## 技術仕様

- **依存関係**: Python標準ライブラリのみ（外部依存なし）
- **エンコーディング検出**: 手動指定（自動検出なし）
- **改行コード**: CRLF/LF/CRを検出し、復元時に再適用
- **バックアップ**: デフォルトで作成、`--no-backup`で無効化可能

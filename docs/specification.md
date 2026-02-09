# charenc 仕様書 (v2.0)

## 概要

AIエージェントで cp932 等の非UTF-8ファイルを編集する際の文字化け問題を解決するスキル。

**ワークフロー**: `cp932ファイル → UTF-8に変換 → 編集 → cp932に戻す`

**v2.0の主な変更**:
- 改行コードの変換を廃止（文字コード変換のみに責務を絞る）
- metadata形式をv2に刷新（`schema: "charenc-simple"`）
- CLIオプションを簡素化

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
| `--no-backup` | バックアップを作成しない | No |

**メタデータ形式 (v2)**:
```json
{
  "schema": "charenc-simple",
  "original_file": "example.txt",
  "original_encoding": "cp932",
  "original_hash": "sha256hash...",
  "converted_hash": "sha256hash...",
  "backup_path": "example.txt.cp932.bak",
  "converted_at": "2026-02-03T10:30:00"
}
```

**注**: v1形式のmetadataは非対応です。

### restore_encoding.py

UTF-8ファイルをメタデータに基づいて元のエンコーディングに復元する。

**機能**:
- UTF-8ファイルをメタデータに基づいて元のエンコーディングに復元
- バックアップとメタデータをクリーンアップ
- ファイル変更検出（ハッシュ検証）

**使用方法**:
```bash
python restore_encoding.py <file>
```

**オプション**:
| オプション | 説明 |
|-----------|------|
| `--errors` | エラー処理: strict/replace/backslashreplace/xmlcharrefreplace (デフォルト: strict) |
| `--keep-backup` | バックアップとメタデータを保持 |

**ハッシュ検証**:
- ハッシュ不一致時は警告を表示して処理を継続
- エラーにはならない（v2.0の仕様）

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

## 改行コードの取り扱い

**v2.0の重要な変更**: charenc は改行コードの変換を行いません。

- ファイルの改行コード（CRLF/LF/CR）はそのまま保持されます
- 改行コードの管理はエディタとGitの設定に委ねます

**推奨設定**:

### .gitattributes（リポジトリ全体）
```gitattributes
* text=auto
*.py text eol=lf
*.bat text eol=crlf
*.sh text eol=lf
```

### エディタ設定
- VSCode: `"files.eol": "\n"` または `"\r\n"`
- 既存ファイルの改行コードを変更しない設定を推奨

### Git設定
- Windows: `git config core.autocrlf true` または `false`
- Linux/macOS: `git config core.autocrlf input`

## 技術仕様

- **依存関係**: Python標準ライブラリのみ（外部依存なし）
- **エンコーディング検出**: 手動指定（自動検出なし）
- **改行コード**: 変換なし（そのまま保持）
- **バックアップ**: デフォルトで作成、`--no-backup`で無効化可能

# charenc (v2.0)

AIエージェントで非UTF-8ファイル（cp932, Shift-JIS, EUC-JP等）を編集するための文字エンコーディング変換スキル。

## 概要

多くのAIエージェント（Claude Code, Codex, Cursor等）はUTF-8で動作するため、cp932等のファイルを直接編集すると文字化けが発生します。
このスキルは「UTF-8に変換 → 編集 → 元のエンコーディングに復元」というワークフローを提供します。

**v2.0の主な変更**:
- シンプルなCLI（不要なオプションを削減）
- 改行コード変換を廃止（CRLF/LF/CRをそのまま保持）
- Metadata v2形式（`schema: "charenc-simple"`）

## インストール

### Agent Skills対応ツール（Claude Code等）

`skills/charenc` フォルダをスキルディレクトリにコピーまたはシンボリックリンクを作成：

```bash
# Windows (Junction)
mklink /D "%USERPROFILE%\.claude\skills\charenc" "c:\path\to\charenc\skills\charenc"

# macOS/Linux
ln -s /path/to/charenc/skills/charenc ~/.claude/skills/charenc
```

### スタンドアロン使用

スクリプトを任意の場所に配置し、直接実行できます。

## 使用方法

### 1. UTF-8に変換

```bash
python scripts/convert_to_utf8.py <file> -e <encoding>
```

例：
```bash
python scripts/convert_to_utf8.py config.txt -e cp932
```

### 2. ファイルを編集

変換後のファイルは UTF-8 になっています。AIエージェントで自由に編集できます。

### 3. 元のエンコーディングに復元

```bash
python scripts/restore_encoding.py <file>
```

## サポートするエンコーディング

- **日本語**: cp932, shift_jis, euc-jp, iso-2022-jp
- **Unicode**: utf-8, utf-16, utf-32
- **Western**: latin-1, cp1252, ascii

詳細は [skills/charenc/references/supported_encodings.md](skills/charenc/references/supported_encodings.md) を参照。

## ライセンス

MIT License

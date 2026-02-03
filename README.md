# charenc

Claude Code で非UTF-8ファイル（cp932, Shift-JIS, EUC-JP等）を編集するための文字エンコーディング変換スキル。

## 概要

Claude Code は UTF-8 で動作するため、cp932 等のファイルを直接編集すると文字化けが発生します。
このスキルは「UTF-8に変換 → 編集 → 元のエンコーディングに復元」というワークフローを提供します。

## インストール

`skills/charenc` フォルダを `~/.claude/skills/` にコピーまたはシンボリックリンクを作成：

```bash
# Windows (Junction)
mklink /D "%USERPROFILE%\.claude\skills\charenc" "c:\path\to\charenc\skills\charenc"

# macOS/Linux
ln -s /path/to/charenc/skills/charenc ~/.claude/skills/charenc
```

## 使用方法

### 1. UTF-8に変換

```bash
python ~/.claude/skills/charenc/scripts/convert_to_utf8.py <file> -e <encoding>
```

例：
```bash
python ~/.claude/skills/charenc/scripts/convert_to_utf8.py config.txt -e cp932
```

### 2. ファイルを編集

変換後のファイルは UTF-8 になっています。Claude Code で自由に編集できます。

### 3. 元のエンコーディングに復元

```bash
python ~/.claude/skills/charenc/scripts/restore_encoding.py <file>
```

## サポートするエンコーディング

- **日本語**: cp932, shift_jis, euc-jp, iso-2022-jp
- **Unicode**: utf-8, utf-16, utf-32
- **Western**: latin-1, cp1252, ascii

詳細は [skills/charenc/references/supported_encodings.md](skills/charenc/references/supported_encodings.md) を参照。

## ライセンス

MIT License

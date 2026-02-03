# Supported Encodings

## Japanese

| Encoding | Aliases | Description |
|----------|---------|-------------|
| cp932 | ms932, mskanji, ms-kanji | Windows Japanese (Shift-JIS extension) |
| shift_jis | sjis, s_jis | Standard Shift-JIS |
| euc-jp | eucjp, ujis | Unix Japanese |
| iso-2022-jp | csiso2022jp | JIS (email encoding) |
| euc-jis-2004 | jisx0213 | JIS X 0213 |

## Unicode

| Encoding | Aliases | Description |
|----------|---------|-------------|
| utf-8 | utf8 | Unicode (default for Claude Code) |
| utf-8-sig | | UTF-8 with BOM |
| utf-16 | utf16 | UTF-16 with BOM |
| utf-16-le | | UTF-16 Little Endian |
| utf-16-be | | UTF-16 Big Endian |
| utf-32 | utf32 | UTF-32 |

## Western

| Encoding | Aliases | Description |
|----------|---------|-------------|
| latin-1 | iso-8859-1 | Western European |
| cp1252 | windows-1252 | Windows Western |
| ascii | us-ascii | 7-bit ASCII |

## Common Use Cases

- **Windows Japanese files**: Use `cp932`
- **Unix/Linux Japanese files**: Use `euc-jp`
- **Email attachments (Japanese)**: Use `iso-2022-jp`

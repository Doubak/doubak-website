# 豆瓣备份器 — logo assets

Colours: tile `#2E963D`, beans `#FFF4D8`.

## Which file where

| File | Use |
|---|---|
| `doubak-icon.svg` | Display master, 128px and up. Both hilums plus 豆 knocked out of the front bean. |
| `doubak-icon-mid.svg` | 24–96px. Both hilums, no 豆 — the glyph's strokes fragment below 128px. |
| `doubak-icon-small.svg` | 16–20px. Bigger beans, wider channel, one hilum instead of two. |
| `doubak-mark.svg` | Beans only, no tile. Fills with `currentColor` — pairs with a wordmark, works on any background. |
| `doubak-maskable.svg` | Full-bleed square for Android adaptive icons and iOS. No corner radius; the platform applies its own mask. |
| `favicon.ico` | 16 + 32 + 48 in one file, for `/favicon.ico`. |
| `png/` | 16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512 + `icon-maskable-512.png`. Each already routed to the right tier. |

## Web

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/doubak-icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/png/icon-180.png">
<link rel="manifest" href="/site.webmanifest">
```

Browsers that support SVG favicons take the second line and ignore the `.ico`;
older ones fall back. The `.ico` stays because some feed readers and crawlers
still request `/favicon.ico` by path regardless of what the markup says.

## Web app manifest

```json
"icons": [
  { "src": "/png/icon-192.png", "sizes": "192x192", "type": "image/png" },
  { "src": "/png/icon-512.png", "sizes": "512x512", "type": "image/png" },
  { "src": "/png/icon-maskable-512.png", "sizes": "512x512",
    "type": "image/png", "purpose": "maskable" }
]
```

## Browser extension (MV3)

Chrome will not accept SVG here — PNG only.

```json
"icons": { "16": "icons/icon-16.png", "32": "icons/icon-32.png",
           "48": "icons/icon-48.png", "128": "icons/icon-128.png" },
"action": { "default_icon": { "16": "icons/icon-16.png",
                              "32": "icons/icon-32.png" } }
```

All four extension sizes come from the small/mid masters, so none of them
carry 豆 — at 48px its thinnest stroke lands under one device pixel.

## Notes

- **Inlining SVG.** Each file carries a mask with an `id` (`dbk-a`, `dbk-s`,
  `dbk-m`, `dbk-k`). If you inline more than one on the same page, rename the
  ids — duplicate ids will cross-wire the masks.
- **How the channel works.** The gap between the beans is not a green stroke; it
  is a genuine hole cut by stroking the front bean's outline inside the mask.
  That is why `doubak-mark.svg` still separates correctly on a background that
  is not `#2E963D`.
- **Regenerating.** `gen_logo.py` builds every file from one bean path plus the
  豆 glyph. `BACK_S` / `FRONT_S` tune the depth ratio, `gap` the channel width,
  `DOU_CENTRE` / `DOU_SIZE` the glyph's position and size within the front bean.
- **Rasterise with `rsvg-convert`, not cairosvg.** cairosvg silently ignores
  every mask in a document that defines more than one, which these files do. It
  produces a plausible-looking icon with no hilums, no 豆, and the beans fused.

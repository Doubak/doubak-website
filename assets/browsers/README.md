# 浏览器标志

首页安装按钮左边那两个图标。**不是豆备自己的标志**——`../logos/` 才是，那一套的说明
在 `../logos/README.md`。

| 文件 | 是什么 | 出处 |
|---|---|---|
| `chrome.svg` | Google Chrome 的单色字形 | [Simple Icons](https://simpleicons.org)（图形文件 CC0-1.0） |
| `edge.svg` | Microsoft Edge 的单色剪影 | 取自 [browser-logos](https://github.com/alrra/browser-logos) 里官方 SVG 的三条轮廓路径，去掉渐变和高光 |

Chrome、Microsoft Edge 及其标志分别是 Google 和 Microsoft 的商标。这里按**指名使用**
的方式用它们：给「安装到 Chrome / Edge」这两个按钮标明各自通向哪个商店，不表示两家
与本项目有任何关联或对它的认可。

## 为什么是单色的

站上的配色只有两档绿加一档灰（见 `css/main.css` 开头）。原版 logo 是彩色带渐变的，
四种品牌色压在实心绿按钮上，看起来像贴上去的贴纸，而不像这一页上的东西。改成单色之后
它们跟着按钮的 `currentColor` 走——绿底上是白的，淡绿底上是绿的——形状还认得出来，
颜色不再和页面打架。

## 怎么用

当 CSS mask 用，**不是** `<img>`：

```css
.btn-chrome { --browser-icon: url(/assets/browsers/chrome.svg); }
```

所以这两个文件里**不要写 `fill`**。mask 只看 alpha：有笔画的地方不透明，
颜色是按钮那边用 `background-color: currentColor` 刷上去的。写死一个 `fill` 不会
让它变色，只会让人以为这里能改颜色。

同理，两个文件的 `viewBox` 不一样（`24` 和 `27600`）也不用统一——mask 是按
`contain` 缩放的，只看比例。

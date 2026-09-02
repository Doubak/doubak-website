# 商店素材

Chrome 应用商店与 Edge 加载项的图片素材。**尺寸是商店定死的**，改之前先查
[官方文档](https://developer.chrome.com/docs/webstore/images)。

| 文件 | 用在哪 | 尺寸 |
|---|---|---|
| `promo-small-440x280.svg` / `.png` | 小型宣传图块 | 440×280 |

## 为什么要有小型宣传图块

不是为了好看。官方文档的原话是：**没有这张图的扩展，会排在有这张图的扩展后面**
（“Extensions that don't have a small promotional image will be shown after
extensions that do have that image.”）。所以它是一个排序惩罚，不是可选的装饰。

**顶部宣传图块（1400×560）故意没做。** 它唯一的作用是让扩展有资格出现在商店首页的
推荐位——而那是 Google 编辑挑的，不是做了图就有。做一张要花真功夫，换来的只是一张
彩票。等真被联系上、或者装机量大到值得再说。

## 改图注意

- **SVG 是源文件，PNG 是产物。** 改 SVG，然后重新渲染，别直接改 PNG。
- **渲染要用真正的 SVG 渲染器**（librsvg / 浏览器 / Inkscape）。ImageMagick 自带的
  MSVG 渲染器**画不出中文，也画不出渐变**——它不会报错，只会给你一张黑底、缺字的图，
  看起来像是设计做坏了。
- **上传的 PNG 不要带透明通道。** 渲染出来默认是带的，记得 flatten。
- SVG 的注释里**不能出现两个连字符连写**（XML 规定），写 CSS 变量名的时候会踩到。

```sh
# 用浏览器或任何真渲染器把 SVG 转成 440×280 PNG 之后：
convert promo-small-440x280.png -background '#0d3319' -alpha remove -alpha off -strip \
        PNG24:promo-small-440x280.png
identify -format '%wx%h 透明通道 %A\n' promo-small-440x280.png   # 应当是 440x280 透明通道 False
```

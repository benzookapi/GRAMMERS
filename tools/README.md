# デジタル版の制作

`build_digital_editions.py` は、ローカルの `_works/No1`〜`No15` にある
PNG原稿から、完全版と第1・2話の試し読み版を作成します。
原稿・生成PDF・商品画像は `.gitignore` によりGit管理の対象外です。

## PDFを作成

Python 3、Pillow、ReportLab、pypdfが必要です。フォントはmacOSの
Arial、Arial Bold、Arial Unicodeを使用します。

```sh
python3 -m pip install Pillow reportlab pypdf
python3 tools/build_digital_editions.py
```

生成先は `output/pdf/`、中間ファイルは `tmp/pdfs/` です。
完全版は180ページ、試し読み版は32ページです。
目次リンク・各話のしおり・ページ順と原稿ハッシュのマニフェストを含みます。
原稿やレイアウトを変更した場合は、生成PDFを表示して確認してください。

## 商品画像を作成

Popplerの `pdftoppm` で各PDFの表紙をPNGに書き出します。
配布するPDF全体を作り直さずに表紙だけを生成する場合は、
`python3 tools/build_digital_editions.py --product-covers-only` を使用できます。

```sh
pdftoppm -f 1 -l 1 -scale-to 1800 -singlefile -png output/pdf/grammers-complete-ja.pdf output/pdf/grammers-complete-cover
pdftoppm -f 1 -l 1 -scale-to 1800 -singlefile -png output/pdf/grammers-free-sample-ja.pdf output/pdf/grammers-sample-cover
```

`build_product_thumbnails.cjs` はNode.jsと `sharp` を使用します。
元の表紙を拡大・縮小せず、左右に白い余白を追加して正方形にします。
出力後に元画像の全ピクセルが一致することを検証します。

```sh
npm install --no-save --package-lock=false --prefix /tmp/grammers-image-tools sharp
NODE_PATH=/tmp/grammers-image-tools/node_modules node tools/build_product_thumbnails.cjs
```

生成先は `output/shopify/grammers-{complete,sample}-cover-square.png` と、
元画像を埋め込んだ同名のSVGです。

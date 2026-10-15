# Presentations

komagataの発表資料カタログです。GitHub Pages のルートに、タイトルとサムネイルから公開先へ移動できる一覧を生成します。

- このサイト：2件（AI Voice Assistant の30枚のビューア、Omarchy Meetup Tokyo Night — Opening の7枚のビューア）
- [Speaker Deck](https://speakerdeck.com/komagata)：18件
- [SlideShare](https://www.slideshare.net/komagata)：14件

外部資料のメタデータ取得日：2026-10-15。公開プロフィールで確認した32件を収録しています。各資料のタイトル、公開日、スライド数、URL、プラットフォームのIDを保持し、サムネイル取得元を `thumbnail_url` に記録しています。資料の追加や削除を定期実行する仕組みはありません。

## ビルド

依存追加は不要です。Python標準ライブラリで、ネットワークに接続せずビルドできます。

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/build_pages.py
node --check site/catalog.js
node --check ai-voice-assistant/web/app.js
```

出力は `_site/`。`--output PATH` で変更できます。公開対象は生成したルートHTML、カタログのJSON・CSS・JS・参照画像、2つのビューアの許可済みファイルだけです。原稿のMarkdown、PDF/PPTX、検証ファイル、未参照画像などはコピーしません。無関係なファイルを含む出力先やソースと衝突する出力先を拒否します。生成後の全ファイルで30MB未満を確認してから出力先を置き換えます。

Pagesのワークフローは `main` の `site/**` などの変更で動きます。AI Voice Assistant の操作・動画・スライド更新方法は [AIビューアの説明](ai-voice-assistant/web/README.md)、Opening の再生成と共有ビューアの構成は [Openingビューアの説明](omarchy-meetup3-opening/web/README.md) を参照してください。Opening の先頭動画はミュートでループ自動再生し、移動時の停止は共有する Reveal ビューアが管理します。AI側の動画は音声ありの手動再生です。

## カタログを更新する

`site/catalog.json` が唯一のメタデータファイルです。`site/index.html` はテンプレートで、ビルド時にすべてのカードをHTMLとして生成します。JavaScriptがなくても34件のリンクを表示し、JavaScriptが有効な場合にだけタイトル検索と公開先フィルターを表示します。

1. 元の公開ページを確認し、`presentations` に1件ずつ追加・修正します。IDはタイトルではなくプラットフォームと元の安定IDから作ります。別の公開先に同じタイトルの資料があっても統合しません（「漬け水に浸かる」は2件）。
2. 外部のリンク先は `https://speakerdeck.com/…` または `https://www.slideshare.net/…` にします。PDFダウンロードや埋め込みには置き換えません。
3. 公開サムネイルを `site/images/<id>.jpg` に保存し、`thumbnail` は `./images/<id>.jpg`、`thumbnail_url` は取得元の完全なHTTPS URLにします。画像もリポジトリに含めるので、通常のビルドでダウンロードは不要です。
4. `date` は `YYYY-MM-DD`、不明なら `null`。`slides` は正の整数、不明なら `null` にします。取得日 `retrieved_at` も更新します。
5. 先頭はローカル2件、その後は公開日の新しい順です。ローカル資料の開催日は確認できていないため `null` のままです。OpeningはHype原稿と同じ7枚です。開催日や説明は推測で追加しません。
6. 上記のテストとビルドを実行し、差分とリンク先を確認します。件数を増やす際は `tools/test_catalog.py` の期待件数も更新してください。

AI Voice Assistant は公開済みの最初のスライドをサムネイルに使用します。Opening は原稿ディレクトリの `images/omarchy-meetup-sunset-road.jpg` を `site/images/opening.jpg` にコピーしたものです。Opening のカードはこのサイトの7枚のWebスライドを開きます。両デッキはAI側のReveal・CSS・JavaScriptを共有するため、生成したサイト全体でプレビューしてください。

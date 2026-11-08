# おれのOmarchyアプリ

komagataが作ったOmarchy向けアプリとWebサイトの紹介。Marpによる16:9・13枚の日本語スライドです。

- [公開スライド](https://komagata.github.io/presentations/ore-no-omarchy-apps/)
- [プレゼンテーション一覧](https://komagata.github.io/presentations/)
- [Marp原稿](ore-no-omarchy-apps.md)
- [PDF](ore-no-omarchy-apps.pdf)

## 内容

OMA、OmaText、Omawser、LINE for Omarchy、Omarchy Upstreamを紹介。Omarchy Tokyo MeetupとDHHの登壇動画、「AI時代のOS Omarchy」のYouTube動画、当日持参するOmarchyキー用シールの話も収録しています。動画スライドにはクリックできる画像とQRコードを付けています。

LINEは非公式・開発中、Omarchy Upstreamは独立運営の非公式Webサイトです。機能説明と検証範囲は作成時に確認した各READMEに基づきます。出典は最終スライドに記載しています。発表者ノートはMarkdownのHTMLコメントです。

## 再生成

Node.js、npm、日本語フォント、PDF出力用のChromiumが必要です。作成時のMarp CLIは4.5.1です。

```sh
cd ore-no-omarchy-apps
npm exec --yes --package=@marp-team/marp-cli@4.5.1 -- marp ore-no-omarchy-apps.md --html -o ore-no-omarchy-apps.html
npm exec --yes --package=@marp-team/marp-cli@4.5.1 -- marp ore-no-omarchy-apps.md --html --pdf --allow-local-files -o ore-no-omarchy-apps.pdf
```

HTMLを直接開く場合も`images/`を隣に置いてください。PDFは単体で閲覧できます。Pagesではビルド済みHTMLと参照画像のみ公開し、原稿とPDFはGitHubリポジトリから取得できます。

## 画像

アプリの画面は各リポジトリのREADME掲載画像、LINEは架空の会話を用いたデモ画像です。Upstreamは公開サイトの画面、シールは本人のX投稿写真です。動画画像は投稿の告知画像とYouTubeサムネイルです。新たな実機動作検証や動画全編の内容検証を行ったという意味ではありません。

# AI時代のOS Omarchy

既存のHypeスライドをMarp形式に移した、全67枚のプレゼンテーションです。文章とスライドの順番を保ち、参照PDFに合わせた白背景とグレー（#595959）の文字をMarkdown内のCSSで指定しています。文章を中央に置く`statement`と、見出しと本文を左上から並べる`content`の2種類のレイアウトを使います。

- `omarchy-for-ai-era.md`: 編集用のMarpソース
- `omarchy-for-ai-era.hype.md`: 変換前のHypeソースをそのまま保存したもの
- `omarchy-for-ai-era.html`: ブラウザで閲覧できる生成済みスライド
- `images/`: スライドが相対パスで参照する画像

## HTMLを生成する

Node.js 18以上とnpmを用意し、このディレクトリで実行します。使用するMarp CLIは **4.5.1** に固定しています。初回の実行にはパッケージを取得するためのネットワーク接続が必要です。グローバルインストールは不要です。

```bash
npx --yes @marp-team/marp-cli@4.5.1 omarchy-for-ai-era.md --html -o omarchy-for-ai-era.html
```

HTMLの生成だけではブラウザは起動しません。HTMLと`images/`を同じディレクトリ構成のまま置いてください。画像はHTMLに埋め込んでいません。

## 閲覧・プレビュー

生成済みの`omarchy-for-ai-era.html`をブラウザで開けます。HTTP経由で閲覧する場合は、次のコマンドでこのディレクトリを配信し、`http://localhost:8000/omarchy-for-ai-era.html`を開きます。

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Markdownを編集しながらMarpのサーバーで確認する場合は、次を実行し、表示されたURLをブラウザで開きます。終了は`Ctrl+C`です。

```bash
npx --yes @marp-team/marp-cli@4.5.1 --html --server .
```

この作業環境でブラウザによる表示確認を行う場合は、Omabox内で行ってください。

## PDFを書き出す場合

PDF出力にはMarp CLIが対応するブラウザが別途必要です。ローカルの画像を読み込むため、信頼できるこのスライドと画像に対してのみ`--allow-local-files`を指定します。

```bash
npx --yes @marp-team/marp-cli@4.5.1 omarchy-for-ai-era.md --pdf --allow-local-files -o omarchy-for-ai-era.pdf
```

この作業環境ではPDF生成もOmabox内で実行してください。今回の成果物にはPDFは含めていません。

## 画像とレイアウト

Hypeの`span`はMarpの`bg cover`、`fit`と画像だけのスライドは`bg contain`へ置き換えています。DHHのアイコンは見出しの下に通常画像として配置しています。日本語フォントの有無で改行位置が変わるため、発表に使う環境でも表示を確認してください。

### statement：文章を中央に置く

1つの段落を上下左右の中央に配置します。見出し記号は使わず、人工的な改行を入れないことで自然に折り返します。強調には`**太字**`を使えます。

```markdown
<!-- _class: statement -->

Omarchy = Omakase + Arch Linux
```

長い文章には`statement compact`を指定できます。表紙だけは`statement cover`を使い、タイトルの段落に続けて署名の段落を置きます。タイトルと署名のまとまりを中央に配置します。

### content：見出しと本文を左上から並べる

最初に`##`のページタイトルを置き、その下に本文、箇条書き、コード、画像などを並べます。全体を左寄せ・上寄せにします。

```markdown
<!-- _class: content -->

## 今日の目的

- みなさんにOmarchyを知ってもらう
- そしてOmarchyに乗り換えてもらう
```

画像のみのスライドは例外です。レイアウトクラスを指定せず、`![bg cover](images/画像名.webp)`または`![bg contain](images/画像名.webp)`を使います。

Marpの記法は[画像構文](https://marpit.marp.app/image-syntax)と[ディレクティブ](https://marpit.marp.app/directives)を参照してください。

イントロ動画はHTMLスライド内でミュート・ループ再生します。手動でも再生できます。VS CodeのMarpプレビューでは `markdown.marp.html` を `all` に設定してください。PDFでは動画は再生されません。

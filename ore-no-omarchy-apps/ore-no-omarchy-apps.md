---
marp: true
theme: default
size: 16:9
paginate: true
title: おれのOmarchy生成物
author: Masaki Komagata
html: true
footer: 'komagata / おれのOmarchy生成物'
style: |
  section { background: #171923; color: #e5e9f0; font-family: 'Noto Sans CJK JP', sans-serif; padding: 54px 68px; font-size: 27px; line-height: 1.65; }
  section::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 7px; background: #a6da95; }
  h1 { color: #e5e9f0; font-size: 53px; letter-spacing: -.04em; margin: 0 0 22px; }
  h2 { color: #c6a0f6; font-size: 25px; font-weight: 500; margin: 0 0 12px; }
  strong { color: #a6da95; }
  a { color: #91d7e3; text-decoration: none; }
  p { margin: 10px 0; }
  ul { padding-left: 1.1em; }
  li { margin: 13px 0; }
  footer { font-size: 14px; color: #8b93aa; bottom: 19px; }
  section::after { color: #8b93aa; font-size: 16px; }
  .eyebrow { font: 17px monospace; color: #a6da95; letter-spacing: .12em; margin-bottom: 18px; }
  .split { display: grid; grid-template-columns: 43% 57%; gap: 30px; align-items: center; }
  .split > * { min-width: 0; }
  .visual { height: 440px; width: 100%; object-fit: contain; }
  .caption { color: #8b93aa; font-size: 14px; margin-top: 12px; }
  .small { font-size: 21px; color: #b5bdd0; }
  .big { font-size: 43px; line-height: 1.5; font-weight: 700; }
  .tag { color: #171923; background: #a6da95; padding: 3px 10px; font-size: 17px; display: inline-block; margin-bottom: 16px; }
  .cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 18px; margin: 36px 0; }
  .card { border-top: 3px solid #c6a0f6; background: #222533; padding: 22px 17px; min-height: 160px; }
  .card b { font-size: 24px; color: #e5e9f0; }
  .card p { font-size: 20px; color: #b5bdd0; }
  .qr { width: 145px; height: 145px; object-fit: contain; margin-top: 15px; }
  .link { font-size: 17px; overflow-wrap: anywhere; }
  table { font-size: 24px; width: 100%; display: table; margin-top: 25px; }
  th { color: #c6a0f6; background: #222533 !important; }
  tr, td { background: #171923 !important; color: #e5e9f0; border-color: #3b4055 !important; }
  section.cover h1 { font-size: 79px; line-height: 1.3; }
  section.cover { background: radial-gradient(ellipse at 85% 25%, #32374e, #171923 65%); }
  section.sources { font-size: 18px; line-height: 1.55; }
  section.sources h1 { font-size: 38px; }
  section.sources p { margin: 6px 0; }
---
<!-- _class: cover -->

<div class="eyebrow">BUILT FOR OMARCHY / BY KOMAGATA</div>

# おれの<br>Omarchy生成物

**OMA / OmaText / Omawser / LINE / Omarchy Upstream**

Masaki Komagata · @komagata

<!-- 今日は自分が作ったOmarchy向けのアプリとWebサイトを紹介します。最後にMeetup、動画、持参したシールの話もあります。 -->

---

<!-- _footer: '' -->
<!-- _paginate: false -->

<div class="big">Omarchy向けに作ったものを紹介します。</div>

---

<div class="split">
<div>
<div class="eyebrow">01 / TALK</div>
<h1>OMA</h1>
<h2>声で話せる、PCの相棒。</h2>
<ul><li>音声会話と字幕</li><li>PC操作をタスクエージェントに依頼</li><li>会話をまたぐローカルの記憶</li></ul>
<p class="small">テーマ色のローポリな顔が目印。[1]</p>
<p class="caption">音声利用にはOpenAI APIキーと別途課金が必要。</p>
</div>
<div><img class="visual" src="images/oma.png" alt="O.M.A.のローポリな顔と会話画面"><p class="caption">O.M.A. = Omarchy Machine Assistant / README掲載の実画面</p></div>
</div>

<!-- 「OmaTextでメモを作って」「Chromiumを使うと覚えて」など、具体的な頼み方を紹介。音声側とタスクエージェント側の認証・課金は別です。操作の確認は全操作を自動遮断する仕組みではないため、安全性を過大に説明しないでください。 -->

---

<div class="split">
<div>
<div class="eyebrow">02 / WRITE</div>
<h1>OmaText</h1>
<h2>テキストを、すぐ書く。</h2>
<ul><li>普通のウィンドウ、最小限のUI</li><li>Omarchyのテーマに追従</li><li>日本語IME・ファイルツリーに対応</li></ul>
<p class="small">タブもMarkdownプレビューも、なし。[2]</p>
<p class="caption">QML + Python標準ライブラリ。利用時のビルド不要。</p>
</div>
<div><img class="visual" src="images/omatext-clean.png" alt="設定アイコンのない最新版OmaTextの画面"><p class="caption">ローカル最新版の実画面 / 設定はCtrl+, / 撮影用サンプル</p></div>
</div>

<!-- メモを書き、Ctrl+Sで保存するデモに向く。ファイルツリーはCtrl+B。自動保存や外部変更監視はないので、終了・再読み込み前に保存してください。 -->

---

<div class="eyebrow">OMATEXT / FILE TREE</div>

# ファイルツリーから、開く。

<img src="images/omatext-tree.png" alt="OmaTextでファイルツリーを表示し、notesフォルダのideas.mdを開いた画面" style="width:100%;height:430px;object-fit:contain">

<div class="caption">Ctrl+Bで表示・非表示を切り替え。ローカル最新版を隔離環境で撮影 / ファイル・文章は撮影用サンプル。</div>

<!-- 実際のQuickshellプラグインを、手元のomatext-keyboard-settings作業ツリーから読み込んで撮影。アプリ本体やユーザーのデスクトップ設定は変更していません。 -->

---

<div class="split">
<div>
<div class="eyebrow">03 / BROWSE</div>
<h1>Omawser</h1>
<h2>Webを、キーボードから。</h2>
<ul><li>1タブなら、ページが主役</li><li>Ctrl+Lでアドレス欄を表示</li><li>タブ切り替えもキーボードで</li></ul>
<p class="small">Omarchyのテーマに追従するブラウザ。[3][7]</p>
<p class="caption">Tauri / WebKitGTK。独立したデスクトップアプリ。</p>
</div>
<div><img class="visual" src="images/omawser.png" alt="OmawserでOmarchyのWebサイトを表示"><p class="caption">README掲載のTokyo Nightテーマでの実画面</p></div>
</div>

<!-- Ctrl+L、Ctrl+T、Ctrl+Tabで操作を見せる。汎用ブラウザの全機能を備えているとは説明しない。カメラ・マイク等の権限要求は拒否する実装で、一部OAuthフローにも制限があります。 -->

---

<div class="split">
<div>
<div class="eyebrow">04 / CHAT</div>
<h1>LINE</h1>
<span class="tag">非公式 / 開発中</span>
<h2>Omarchyでも、チャット。</h2>
<ul><li>チャット・返信・添付・スタンプ</li><li>日本語 / EnglishのUI</li><li>QML + Goのプラグイン</li></ul>
<p class="small">LINE公式の製品ではありません。[4]</p>
<p class="caption">READMEでは実送信・相手への到達は未検証。</p>
</div>
<div><img class="visual" src="images/line.png" alt="LINEプラグインの架空データによるデモ画面"><p class="caption">架空の人物・会話を使ったデモ画面</p></div>
</div>

<!-- 画面と実装済みの機能を紹介。保存済みアカウントでチャット等の確認記録はあるが、QRでの再ログイン、実メッセージ送信、相手への配達はREADME上では未検証。安定した公式クライアントの代替と断定しない。 -->

---

<div class="split">
<div>
<div class="eyebrow">05 / FOLLOW DEVELOPMENT</div>
<h1 style="font-size:46px">Omarchy<br>Upstream</h1>
<h2>開発の動きを、読み物に。</h2>
<ul><li>PR・コミット・議論をまとめる</li><li>日本語を含む10言語</li><li>出典と変更の状態を示す</li></ul>
<p class="small">独立運営・非公式のWebサイト。[5][6]</p>
<p class="link"><a href="https://ja.omarchyupstream.com/">ja.omarchyupstream.com</a></p>
</div>
<div><img class="visual" src="images/upstream.png" alt="Omarchy Upstreamの日本語ホームページ"><p class="caption">公開サイトのスクリーンショット / アプリではなくWebサイト</p></div>
</div>

<!-- 正式表記はOmarchy Upstream。実装済みと提案中を区別して読むためのサイト。AI支援による編集・翻訳を行いますが、品質を無条件に保証するとは説明しません。 -->

---

<div class="split">
<div>
<div class="eyebrow">COMMUNITY / TOKYO</div>
<h1 style="font-size:45px">Omarchy Tokyo<br>Meetupも開催。</h1>
<p class="big">DHHも来た！</p>
<p>登壇動画をYouTubeで公開しています。[11][12]</p>
<p class="small">Omarchy Quattro RS 4.5 Live Demo - DHH</p>
<a href="https://www.youtube.com/watch?v=bMrbS98gGIk"><img class="qr" src="images/meetup-qr.png" alt="DHH登壇動画の視聴用QRコード"></a>
</div>
<div><a href="https://www.youtube.com/watch?v=bMrbS98gGIk"><img class="visual" src="images/meetup.jpg" alt="DHH登壇動画のYouTubeサムネイル"></a><p class="caption">Omarchy Tokyoチャンネル / QRコード・画像から動画へ</p></div>
</div>

<!-- ユーザー提供の開催・来場の説明に基づくスライド。投稿ではMeetupでのDHH登壇動画の公開を確認。開催日・人数等は未確認なので加えていません。 -->

---

<div class="split">
<div>
<div class="eyebrow">WATCH ON YOUTUBE</div>
<h1 style="font-size:45px">AI時代のOS<br>Omarchy</h1>
<p>Omarchyを知らない人向けに、<br><strong>約2時間</strong>話しました。[9]</p>
<p>YouTubeで見られます！</p>
<a href="https://www.youtube.com/watch?v=roFx9CB_yn0"><img class="qr" src="images/youtube-qr.png" alt="AI時代のOS Omarchyの視聴用QRコード"></a>
<p class="caption">フィヨルドブートキャンプのチャンネル [10]</p>
</div>
<div><a href="https://www.youtube.com/watch?v=roFx9CB_yn0"><img class="visual" src="images/youtube.jpg" alt="AI時代のOS Omarchyの告知画像"></a><p class="caption">QRコード・画像をクリックして視聴できます</p></div>
</div>

<!-- 正確な再生時間の計測ではなく、本人の投稿「2時間ぐらい」に沿った表現です。動画内容の要約は行っていません。 -->

---

<div class="split">
<div>
<div class="eyebrow">OMARCHY SONG</div>
<h1 style="font-size:34px;white-space:nowrap">Omarchyの歌を作りました</h1>
<p>ここで、ちょっと聴いてください。[13]</p>
<p style="margin-top:30px"><a href="https://x.com/komagata/status/2110654529209511966" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#a6da95;color:#171923;padding:14px 20px;font-weight:bold">▶ 歌を開いて再生する</a></p>
<p class="link" style="margin-top:20px"><a href="https://x.com/komagata/status/2110654529209511966" target="_blank" rel="noopener noreferrer">https://x.com/komagata/status/2110654529209511966</a></p>
</div>
<div><a href="https://x.com/komagata/status/2110654529209511966" target="_blank" rel="noopener noreferrer"><img class="visual" src="images/omarchy-song.jpg" alt="Omarchyの歌の動画サムネイル"></a><p class="caption">ボタン・画像・URLからXの投稿を開けます</p></div>
</div>

<!-- 発表中にボタンをクリックして投稿を別タブで開き、動画の再生ボタンを押す。自動再生は設定していません。 -->

---

<div class="split">
<div>
<div class="eyebrow">ONE MORE THING</div>
<h1 style="font-size:46px">キーのシールを<br>作りました。</h1>
<p class="small">Omarchyキー用のシール。[8]</p>
<p style="font-size:35px;line-height:1.6;margin-top:28px">今日持ってきているので、<br><strong>貼らせてください！</strong></p>
<p class="caption">貼っていい方、ぜひ声をかけてください。</p>
</div>
<div><img class="visual" src="images/stickers-1.jpg" alt="Omarchyキー用シールの写真"><p class="caption">本人のX投稿に掲載した写真</p></div>
</div>

<!-- 持参していることと「貼らせてください」は本人の指定。希望する方だけに貼らせてもらう、という温度感で締めます。 -->

---
<!-- _class: cover -->
<!-- _footer: '' -->
<!-- _paginate: false -->

# Thank you!

---
<!-- _class: sources -->

# Sources

[1] https://github.com/komagata/oma
[2] https://github.com/komagata/OmaText
[3] https://github.com/komagata/omawser
[4] https://github.com/komagata/line
[5] https://ja.omarchyupstream.com
[6] https://github.com/komagata/omarchy-upstream
[7] https://github.com/komagata/omawser/blob/main/docs/browser.md
[8] https://x.com/komagata/status/2118891648675709352
[9] https://x.com/komagata/status/2118509671204134973
[10] https://www.youtube.com/watch?v=roFx9CB_yn0
[11] https://x.com/komagata/status/2118160669300400325
[12] https://www.youtube.com/watch?v=bMrbS98gGIk
[13] https://x.com/komagata/status/2110654529209511966

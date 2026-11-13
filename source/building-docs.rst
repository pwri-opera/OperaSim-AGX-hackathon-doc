============================
このマニュアルのビルド方法
============================

この章は、このマニュアル自体を HTML にビルドする方法を説明します。マニュアルを更新する人向けの内容で、ハッカソンの参加者が読む必要はありません。Python **3.11 以上** が必要です（Sphinx 8.2 系の要件です）。

図の描画に必要なもの
----------------------

構成図と状態遷移図は、Sphinx 標準の ``sphinx.ext.graphviz`` 拡張で SVG に描画します。Python の依存パッケージに加え、Graphviz の ``dot`` コマンドと日本語フォントが必要です。Ubuntu では次のようにインストールします。

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y graphviz fonts-noto-cjk
   dot -V

macOS と Windows でも Graphviz をインストールし、 ``dot`` に PATH を通してください。図では ``Noto Sans CJK JP`` を指定しています。同フォントを用意するか、日本語を表示できるフォントへ図の ``fontname`` を変更してください。SVG を別の端末で閲覧するときも、日本語フォントが必要です。

Read the Docs では、 ``.readthedocs.yaml`` の ``build.apt_packages`` に Graphviz と日本語フォントを指定しているため、ビルド時にインストールされます。拡張の仕様は `Sphinx の Graphviz ドキュメント <https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html>`_ を参照してください。

Linux と macOS の場合
-----------------------

リポジトリのルートで仮想環境を作り、依存パッケージをインストールして、ビルドします。

.. code-block:: bash

   python3 -m venv .venv-docs
   .venv-docs/bin/pip install -r requirements.txt
   .venv-docs/bin/python -m sphinx -n -W --keep-going -b html source build/html

``requirements.txt`` には、 ``Sphinx>=8.2,<9`` と ``sphinx-rtd-theme>=3,<4`` が書かれています。 ``-n`` は、解決できない参照を警告にするオプションです。 ``-W`` は、警告をエラーとして扱うオプションで、参照の誤りがあるとビルドが失敗します。 ``--keep-going`` は、最初のエラーで止まらず、残りも処理してから、まとめて報告させるオプションです。なお、これらが確認するのは、 **ドキュメント内の参照と記法** だけです。外部の URL が有効かどうかは確認しません。外部リンクの切れは、HTML のビルドでは検出できません。

``make`` を使う場合は、仮想環境を有効にしてから実行します。

.. code-block:: bash

   source .venv-docs/bin/activate
   make html
   make clean    # build 以下の成果物を削除します

Windows（PowerShell）の場合
-----------------------------

.. code-block:: powershell

   py -3 -m venv .venv-docs
   .\.venv-docs\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv-docs\Scripts\python.exe -m sphinx -n -W --keep-going -b html source build\html

出力と確認
------------

ビルド結果は、 ``build/html/index.html`` に出力されます。ブラウザで開くか、簡易サーバーで確認します。

.. code-block:: bash

   python3 -m http.server --bind 127.0.0.1 -d build/html 8000
   # → http://localhost:8000

``.venv-docs`` と ``build/`` は、ローカルで生成されるファイルです。 ``.gitignore`` で除外してあるので、リポジトリには含めません。

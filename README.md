# OperaSim-AGX ハッカソン セットアップガイド

Windows の Unity シミュレータと Linux の ROS 2 Humble ミドルウェアを使う、ハッカソン参加者向けのマニュアルです。コードを開発する場合は、Ubuntu 22.04 に ROS 2 をインストールします。まず動きを試す場合は、ホストに ROS 2 を入れずに [Docker でサンプルを実行できます](source/sample-run.rst)。

- [マニュアルの目次](source/index.rst)
- [ビルド方法](source/building-docs.rst)
- [シミュレータ本体（hackathon ブランチ）](https://github.com/pwri-opera/OperaSim-AGX/tree/hackathon)

## ローカルビルド

Python 3.11 以上と、図の描画用のGraphviz・日本語フォントを使います。Ubuntuでは、先に `sudo apt-get install -y graphviz fonts-noto-cjk` を実行してください。他のOSでの準備は[ビルド方法](source/building-docs.rst)を参照してください。

```bash
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements.txt
.venv-docs/bin/python -m sphinx -n -W --keep-going -b html source build/html
```

出力は `build/html/index.html` です。

## Read the Docs

[OperaSim-AGX-doc](https://github.com/pwri-opera/OperaSim-AGX-doc) を参考に、`source/` 構成、日本語の `sphinx_rtd_theme`、Ubuntu 22.04 / Python 3.12 の設定を使用しています。

Read the Docs でこのリポジトリをインポートし、デフォルトブランチを `main`、言語を日本語に設定すると、`.readthedocs.yaml` に従ってビルドできます。公開 URL は Read the Docs 側でのプロジェクト作成後に確定します。

原稿は OperaSim-AGX のハッカソン向け `docs/` をもとにしています。Windows のシミュレータと Linux のミドルウェアを実際に接続する動作検証は行っていません。

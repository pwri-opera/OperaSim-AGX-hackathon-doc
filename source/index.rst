============================================
OperaSim-AGX ハッカソン セットアップガイド
============================================

OperaSim-AGX ハッカソンに参加する開発者向けのマニュアルです。Windows PC の Unity シミュレータを Linux PC の ROS 2 ミドルウェアに接続します。サンプルの実行と、自律制御コードの開発に必要な手順を案内します。

.. note::

   このリポジトリはマニュアル専用です。セットアップ手順に出てくる ``Assets/`` 、 ``ProjectSettings/`` 、 ``docker-hackathon-sample/`` は、 `シミュレータ本体の hackathon ブランチ <https://github.com/pwri-opera/OperaSim-AGX/tree/hackathon>`_ 内のパスです。ソース版での起動やサンプルの実行には、本体のリポジトリが別途必要です。

.. note::

   画面名、メニュー名、ボタン名は、画面に表示される英語のまま記載しています。Unity Editor と AGX Dynamics のバージョンは、シミュレータ本体の ``ProjectSettings/ProjectVersion.txt`` と ``Assets/AGXUnity/package.json`` に基づいています。ハッカソン運営から別の配布物や指示があった場合は、そちらを優先してください。

.. note::

   手順はソースコードと公式ドキュメントに基づいています。Windows の Unity と Linux の ROS 2 を実際に接続する動作検証は行っていません。動作が記載と異なる場合は、最新の公式情報と運営の案内に従ってください。

事前準備
----------

ハッカソン参加者は、 `土木研究所の募集要項 <https://www.pwri.go.jp/team/advanced/opera-hackathon-2.html>`_ に従い、開催日までに開発環境を構築し、動作を確認してください。

**ハッカソン当日は、シミュレータのセットアップと AGX ライセンス認証が済んだ会場の Windows PC を利用できます。** 参加者が Windows PC を持参したり、当日のために AGX ライセンスを申請・認証したりする必要はありません。下の Windows セットアップとライセンスの手順は、自分で用意した PC で事前検証する場合だけ参照してください。

1. :ref:`participant-laptop` を確認し、会場へ持参する Linux ノート PC を用意します。
2. 運営が GitHub で案内する Docker イメージと環境構築手順を使います。このマニュアルの Docker サンプルはソースからビルドする別手順です。公開要項には配布イメージの識別子が記載されていないため、同じイメージとはみなさないでください。Linux ホストに ROS 2 を直接入れる手順も、公式の事前準備の代わりにはなりません。
3. 運営指定の手順で動作を確認します。下記のサンプルを使う場合は :ref:`sample-run-checklist` で一巡したことを確認できます。案内が見つからない場合や動作しない場合は :ref:`participant-support` を参照してください。

システム構成
--------------

シミュレータとミドルウェアは TCP で接続します。構成は次のとおりです。

- **Windows PC（シミュレータ側）**：Unity 2022.3.62f3 と AGX Dynamics for Unity で動く OperaSim-AGX です。Unity Editor で Play するか、運営が配布するビルド済みプレイヤーを実行します。
- **Linux PC（ミドルウェア側）**：Ubuntu 22.04 に ROS 2 Humble を直接インストールして動かす自律制御スタックです。一連の動きを手軽にテストする Docker 環境は :doc:`sample-run` で案内します。
- **接続**：Linux 側の ``ros_tcp_endpoint`` が TCP ポート 10000 で待ち受け、Windows 側の ROS-TCP-Connector がそこへ接続します。2 台は同じ LAN 上に置いてください。

建機の ROS 名前空間は、シーン内の GameObject 名がそのまま使われます。ハッカソンのサンプルでは、 ``/zx200`` が油圧ショベル、 ``/ic120_0`` がクローラダンプです。ただしシーンやセーブデータによって名前が変わることがあるため、実際のトピック名は ``ros2 topic list`` で確認してください。

自分の PC で事前検証する場合
------------------------------

1. **配布物を確認する**：本体のリポジトリ、ビルド済みプレイヤー、ライセンスの手配方法を :doc:`prerequisites` で確認します。
2. **AGX ライセンスを確認する**：事前検証に使う Windows PC に有効なライセンスがなければ、 :doc:`agx-license` に従って手配・認証します。
3. **Windows 側をセットアップする**：配布バイナリ版かソース版かを選び、 :doc:`windows-setup` に従います。

Windows 側のセットアップが終わったら、試したいことに合わせて Linux 側の手順を選びます。どちらも上の「事前準備」とは別の手順です。

- **Docker でまず試す**： :doc:`sample-run` に従って、Windows と Linux の通信を確認し、サンプルを実行します。Linux ホストへの ROS 2 のインストールは不要です。
- **Linux ホストで開発する**： :doc:`linux-middleware` に従って ROS 2 をインストールし、通信を確認してサンプルを実行します。コードの編集と再ビルドは :doc:`development` を参照してください。

.. toctree::
   :maxdepth: 2
   :caption: 目次

   prerequisites
   agx-license
   windows-setup
   simulator-operation
   linux-middleware
   machines-and-field
   sample-run
   sample-implementation
   scoring
   development
   troubleshooting
   building-docs

各章の内容
------------

.. list-table::
   :header-rows: 1
   :widths: 2 5

   * - 章
     - 内容
   * - :doc:`prerequisites`
     - 2 台の PC の役割、必要なバージョン、ネットワーク要件、運営に確認しておくこと
   * - :doc:`agx-license`
     - AGX Dynamics for Unity の評価版の申請と、エディタ版・スタンドアロン版それぞれのアクティベーション
   * - :doc:`windows-setup`
     - 配布バイナリを使う方法と、ソースから Unity プロジェクトをビルドする方法
   * - :doc:`simulator-operation`
     - シミュレータの起動、カメラ操作、セーブ・ロード・リセット、安全な停止方法
   * - :doc:`linux-middleware`
     - ホストへの ROS 2 の導入、ワークスペースのビルド、endpoint の起動、IP アドレスとファイアウォールの確認
   * - :doc:`machines-and-field`
     - ZX200・IC120 の作業能力と、土木研究所の建設 DX 実験フィールドでの実機実験
   * - :doc:`sample-run`
     - Docker 環境の準備と、Windows と接続してサンプルシナリオを動かす通し手順
   * - :doc:`sample-implementation`
     - サンプルのパッケージ構成、起動と状態遷移、Nav2・荷台制御の流れ、改造の入口
   * - :doc:`scoring`
     - シミュレータの加点・減点項目と、正式な競技ルールの確認先
   * - :doc:`development`
     - ホスト上の ``~/opera-ws`` での ROS 2 開発、トピックの確認、非常停止、シミュレーション時計の注意点
   * - :doc:`troubleshooting`
     - 症状別の確認ポイントと対処
   * - :doc:`building-docs`
     - このマニュアル自体のビルド方法（マニュアルを更新する人向け）

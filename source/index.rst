============================================
OperaSim-AGX ハッカソン セットアップガイド
============================================

このマニュアルは、OperaSim-AGX ハッカソンに参加する開発者向けのガイドです。Windows PC 上の Unity シミュレータと Linux PC 上の ROS 2 ミドルウェアを接続し、サンプルシナリオを動かして、自分の自律制御コードを開発するところまでの手順を説明します。

.. note::

   このリポジトリはマニュアル専用です。以降のセットアップ手順に登場する ``Assets/`` 、 ``ProjectSettings/`` 、 ``docker-hackathon-sample/`` などは、 `シミュレータ本体のリポジトリ <https://github.com/pwri-opera/OperaSim-AGX>`_ 内のパスを指します。シミュレータ本体は別途クローンしてください。

.. note::

   画面名、メニュー名、ボタン名などの UI 表記は、英語のまま記載しています。Unity Editor と AGX Dynamics のバージョンは、このリポジトリの設定ファイル（ ``ProjectSettings/ProjectVersion.txt`` と ``Assets/AGXUnity/package.json`` ）に基づいています。ハッカソン運営から別の配布物や指示があった場合は、そちらを優先してください。

.. note::

   このマニュアルの手順は、リポジトリのソースコードと各社の公式ドキュメントをもとに書いています。Windows の Unity と Linux の ROS 2 を実際に接続して動かすエンドツーエンドの検証は、このドキュメントを追加した変更の中では行っていません。実機の挙動が記載と異なる場合は、最新の公式情報と運営の案内に従ってください。

システム構成
--------------

シミュレータとミドルウェアは TCP で接続します。構成は次のとおりです。

- **Windows PC（シミュレータ側）**：Unity 2022.3.62f3 と AGX Dynamics for Unity で動く OperaSim-AGX です。Unity Editor で Play するか、運営が配布するビルド済みプレイヤーを実行します。
- **Linux PC（ミドルウェア側）**：Ubuntu 22.04 に ROS 2 Humble を直接インストールして動かす自律制御スタックです。一連の動きを手軽にテストする Docker 環境は :doc:`sample-run` で案内します。
- **接続**：Linux 側の ``ros_tcp_endpoint`` が TCP ポート 10000 で待ち受け、Windows 側の ROS-TCP-Connector がそこへ接続します。2 台は同じ LAN 上に置いてください。

建機の ROS 名前空間は、シーン内の GameObject 名がそのまま使われます。ハッカソンのサンプルでは、 ``/zx200`` が油圧ショベル、 ``/ic120_0`` がクローラダンプです。ただしシーンやセーブデータによって名前が変わることがあるため、実際のトピック名は ``ros2 topic list`` で確認してください。

最初に行うこと
----------------

1. **配布物の確認**：運営から何が配布されるか（リポジトリ、ビルド済みプレイヤー、ライセンスの手配方法など）を確認します。詳しくは :doc:`prerequisites` を参照してください。
2. **AGX ライセンスの取得とアクティベーション**：ベンダーへの評価版の申請と、シミュレータ PC でのアクティベーションは別々の手順です。 :doc:`agx-license` を参照してください。
3. **Windows 側のセットアップ**：バイナリ版とソース版のどちらかを選び、 :doc:`windows-setup` に従ってシミュレータを起動できる状態にします。
4. **Linux 側のセットアップ**： :doc:`linux-middleware` に従って ROS 2 と依存パッケージを導入し、ホスト上でビルドして endpoint を起動します。
5. **疎通確認とサンプルの実行**： 手軽に一連の動きをテストしたい場合は、Docker を使う :doc:`sample-run` に進みます。
6. **自分のコードの開発**： :doc:`development` で、ホスト上のワークスペースでの編集と再ビルド、トピックの調べ方、非常停止の送り方を確認します。

.. toctree::
   :maxdepth: 2
   :caption: 目次

   prerequisites
   agx-license
   windows-setup
   simulator-operation
   linux-middleware
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

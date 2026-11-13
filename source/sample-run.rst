==================================================
Docker でサンプルシナリオを通し実行
==================================================

この章では、一連の動きを手軽にテストするため、Docker 内の Linux ミドルウェアと Windows のシミュレータを接続して、ハッカソンのサンプルシナリオを最初から最後まで動かします。各手順の見出しに、どのマシンのどの端末で実行するかを書いています。

サンプル内部の構成と、各工程が完了通知で進む仕組みは :doc:`sample-implementation` を参照してください。

.. note::

   ``192.168.x.y`` などの IP アドレスは、例として示しているものです。実際には、 ``ip addr`` などで確認した Linux PC の IP アドレスに置き換えてください。リポジトリは ``$HOME/OperaSim-AGX`` にクローンした前提で説明します。別の場所にクローンした場合は、パスを読み替えてください。 ``<Linux側IP>`` も、実際の値に置き換えてください。

前提
------

- :doc:`windows-setup` のセットアップが終わっていること。ホストに ROS 2 を導入する :doc:`linux-middleware` の作業は、この Docker でのテストには不要です。
- Windows PC と Linux PC が、同じ LAN にあること
- Linux 側に Ubuntu 22.04 と X11 の GUI 環境があること
- ホスト側の endpoint が動いていないこと（TCP 10000 番ポートの競合を避けます）

ホスト側の準備
----------------

- **OS**：Ubuntu 22.04 を推奨します。
- **Docker**：公式の Ubuntu 向けインストールガイド（ `Docker Engine install on Ubuntu <https://docs.docker.com/engine/install/ubuntu/>`_ ）に従ってインストールし、 ``docker version`` と ``docker info`` で動作を確認します。
- **git と python3-venv** （リポジトリのクローンと rocker のインストールに必要です）：

  .. code-block:: bash

     sudo apt-get update
     sudo apt-get install -y git python3-venv

- **リポジトリのクローン**： ``docker-hackathon-sample/`` は、このリポジトリの中にあります。すでにクローン済みの場合は、この手順を飛ばしてください。

  .. code-block:: bash

     git clone https://github.com/pwri-opera/OperaSim-AGX.git "$HOME/OperaSim-AGX"

  ハッカソンで別の URL が指定されている場合は、そちらを使い、以降の手順ではクローン先のパスを読み替えてください。

- **sudo なしで docker を使えるようにする**：起動スクリプトは ``docker`` を直接呼び出します。公式の Linux 向け設定手順（ `Docker Engine post-installation steps <https://docs.docker.com/engine/install/linux-postinstall/>`_ ）に従って、自分のユーザーを ``docker`` グループに追加してください。 ``docker`` グループは、実質的に root と同等の権限を持ちます。ソケットの ``chmod`` ではなく、グループの設定を使ってください。
- **rocker**：GUI（X11）をコンテナに渡すために使います。公式は ``pip`` でのインストールを案内しています。仮想環境にインストールして、PATH を通すのが確実です。

  .. code-block:: bash

     python3 -m venv "$HOME/.venvs/opera-rocker"
     "$HOME/.venvs/opera-rocker/bin/python" -m pip install rocker
     export PATH="$HOME/.venvs/opera-rocker/bin:$PATH"
     rocker --help

  ``export PATH`` は、ホストで新しいターミナルを開くたびに実行し直してください（ ``source "$HOME/.venvs/opera-rocker/bin/activate"`` でも構いません）。ソースコードは `osrf/rocker <https://github.com/osrf/rocker>`_ を参照してください。

  ``apt`` の ``python3-rocker`` が使えるのは、ROS の apt リポジトリを設定済みの環境だけです。何も設定していない Ubuntu で ``apt install python3-rocker`` だけを実行すると、依存関係が解決できずに失敗することがあります。上の pip の手順を使ってください。
- **NVIDIA Container Toolkit**： ``start-nvidia.sh`` を使うときだけ必要な、任意のコンポーネントです。公式のインストールガイド（ `NVIDIA Container Toolkit install guide <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html>`_ ）を参照してください。CPU で描画する場合は不要です。

イメージのビルド
------------------

``$HOME/OperaSim-AGX/docker-hackathon-sample/`` に移動して、 ``build.sh`` を実行します。内部では ``docker build -t opera-hackathon-sample .`` が実行され、ベースイメージ ``osrf/ros:humble-desktop-full`` の上に、ROS 2 のパッケージのインストールと、7 つのリポジトリのクローンとビルドが行われます。

.. code-block:: bash

   cd "$HOME/OperaSim-AGX/docker-hackathon-sample"
   ./build.sh

Dockerfile がクローンするリポジトリとブランチは、次のとおりです。これが、サンプルの標準の構成です。

.. list-table::
   :header-rows: 1
   :widths: 3 2

   * - リポジトリ
     - ブランチ
   * - Unity-Technologies/ROS-TCP-Endpoint
     - ``main-ros2``
   * - pwri-opera/ic120_ros2
     - ``feature/tmp_ic120_unity_setting``
   * - Ryoya1012/Opera-sim_hackathon-Sample
     - ``main``
   * - Ryoya1012/ZX200_autonomy_state_machine
     - ``hackathon``
   * - Ryoya1012/Opera-sim_ic120_hackathon
     - ``main``
   * - pwri-opera/com3_ros
     - ``main``
   * - pwri-opera/gnss_localizer_ros2
     - ``main``

ビルド対象のパッケージは、次の 7 つです。

``ic120_navigation task_manager zx200_autonomy ic120_autonomy ic120_unity com3_msgs ros_tcp_endpoint``

``colcon build --symlink-install --packages-up-to`` で、依存パッケージもまとめてビルドされます。 ``waypoints.csv`` は、イメージ内の ``/ws/waypoints.csv`` にコピーされます。

コンテナの起動
----------------

.. code-block:: bash

   cd "$HOME/OperaSim-AGX/docker-hackathon-sample"
   ./start.sh            # CPU / X11
   # または
   ./start-nvidia.sh     # NVIDIA GPU / X11

どちらも、 ``rocker --name opera-hackathon-sample --x11 --network host --user --home`` で起動します。 ``--network host`` により、コンテナはホストのネットワークを共有するので、endpoint の 10000 番ポートが、そのまま外部から見えます。

.. note::

   ``start.sh`` と ``start-nvidia.sh`` の違いは、 **Linux 側の ROS の GUI（RViz など）の描画に GPU を使うかどうか** だけです。Windows 側の Unity シミュレータの描画や AGX の物理演算には、関係しません。Unity 側が重いときに ``start-nvidia.sh`` を選んでも、改善しません。Windows 側の負荷を下げるには、まず Sim Speed を x1.0 にしてください（ :doc:`simulator-operation` を参照）。

.. warning::

   ``start.sh`` と ``start-nvidia.sh`` は、 ``/ws`` を **バインドマウントしていません** 。コンテナ内の ``/ws`` は、イメージに入っている内容そのままです。コンテナを作り直すと、 ``/ws`` に加えた変更は失われます。自分のコードを開発するときは、 :doc:`linux-middleware` と :doc:`development` のホスト上のワークスペースを使ってください。

別のターミナルから同じコンテナに入るには、次のコマンドを使います。

.. code-block:: bash

   ./enter.sh
   # 中身は docker exec -ti opera-hackathon-sample /ros_entrypoint.sh /bin/bash

手順
------

**1. Linux：コンテナを起動します** （Linux のホストのシェル）

.. code-block:: bash

   cd "$HOME/OperaSim-AGX/docker-hackathon-sample"
   ./start.sh        # CPU の場合。GPU を使う場合は ./start-nvidia.sh

コンテナがすでに起動している場合は、この手順は不要です（ ``docker ps`` で確認できます）。

**2. Linux：endpoint を起動します** （ ``./start.sh`` で開いたコンテナ内のシェル。これをターミナル 1 とします）

.. code-block:: bash

   source /ws/install/setup.bash
   ros2 launch ros_tcp_endpoint endpoint.py

待ち受けが始まったことを、ホスト側の別のターミナルで確認します。

.. code-block:: bash

   ss -tln | grep 10000

**3. Windows：シミュレータを起動して、ROS に接続します** （Windows 側）

配布バイナリの場合は、exe を起動します。ソース版の場合は、Unity Editor で ``GameScene`` を開いて Play します。セットアップ画面が表示されたら、必要に応じて Dump truck Settings や Camera Settings で配置を確認します（最初は、初期配置のままで構いません）。

- ソース版や自作ビルドで ``Connect On Start`` を無効にしている場合：HUD の ROS 設定欄に、IP アドレス（ ``<Linux側IP>`` ）とポート（ ``10000`` ）を入力して、 **Connect** を押します。Protocol を選ぶ欄は HUD にありません。ビルド時とエディタ上で、あらかじめ **ROS2** に設定されている必要があります（設定されていない場合は、ソース側で設定してビルドし直してください）。
- 自動接続が有効なビルドの場合：接続先が正しく埋め込まれているかを、起動ログで確認します（ :ref:`windows-ros-ip` を参照してください）。

**4. Windows：Sim Speed を x1.0 にして、Start Simulation を押します**

**Start Simulation** を押す前に、まず **Sim Speed** を **x1.0** にします。Sim Speed は Start Simulation を押したときに適用され、開始後に変更することはできません。変えたいときは、シミュレーションを停止してリセットし、次の実行で選び直します。実行中にスコアを見たい場合は、 **Total Score** も開始前にオンにします。カメラを選びたい場合も、このセットアップ画面のうちに **Camera Selection** で選んでおきます（開始後は、このメニューは消えます。実行中は、 **C** キーでカメラを順番に切り替えられます）。そのあと、 **Start Simulation** を押します。内部では ``GlobalVariables.changeActionMode(3)`` が呼ばれ、AGX の物理ステップが有効になります。Unity のログに ``Physics Start!`` が出ていることを確認してください。出ていなければ、物理シミュレーションは始まっていません。

**5. Windows と Linux がつながっていることを確認します** （コンテナ内の別のシェル）

``ros2 topic list`` にトピックが表示されるだけでは、接続できている証拠にはなりません。endpoint のログにトピックの登録が出ていることと、実際にフィードバックが流れていることを確認します。

まず、ホスト側の別のターミナルで、コンテナに入ります。

.. code-block:: bash

   cd "$HOME/OperaSim-AGX/docker-hackathon-sample"
   ./enter.sh
   # または: docker exec -it opera-hackathon-sample /ros_entrypoint.sh /bin/bash

endpoint のログに、 ``RegisterPublisher`` や ``RegisterSubscriber`` で ``/<機体名>/...`` の登録が OK と出ていることを確認します。そのうえで、コンテナ内で次のコマンドを実行します。

.. code-block:: bash

   source /ws/install/setup.bash
   ros2 topic list | sort
   ros2 topic info /zx200/joint_states
   ros2 topic echo /ic120_0/joint_states --once

``ros2 topic hz`` は、値を出し続けます。確認できたら ``Ctrl+C`` で止めてください。

.. code-block:: bash

   ros2 topic hz /zx200/joint_states    # Ctrl+C で終了します

``/zx200`` と ``/ic120_0`` の名前空間を持つトピック（ ``/zx200/joint_states`` 、 ``/ic120_0/joint_states`` 、 ``/zx200/odom_pose`` 、 ``/ic120_0/global_pose`` など）が表示され、 ``hz`` や ``echo`` で実際の値が返ってくれば、Windows と Linux の通信は成立しています。名前はシーンやセーブデータによって変わることがあるので、実際の一覧で確認してください。

**6. Linux：サンプルのタスクを起動します** （コンテナ内の、ターミナル 2）

Windows 側の接続とフィードバックを確認してから、起動してください。endpoint より先に自律側を動かすと、指令が届かずに捨てられたり、タスクが途中の状態で残ったりします。

ターミナル 2 は、ホスト側のさらに別のターミナルで開きます。

.. code-block:: bash

   cd "$HOME/OperaSim-AGX/docker-hackathon-sample"
   ./enter.sh
   # または: docker exec -it opera-hackathon-sample /ros_entrypoint.sh /bin/bash

コンテナ内で、次のコマンドを実行します。

.. code-block:: bash

   source /ws/install/setup.bash
   ros2 launch task_manager hackathon_sample.launch.py

ログに、タスクマネージャの準備ができたことを示す出力が出ることを確認してください。

**7. サンプルの進行を見守ります**

タスクマネージャは、まず zx200 が掘削と積み込みを行い、そのあと ic120 が運搬、排土、帰還を行う順で進めます。ic120 がしばらく動かなくても、最初の掘削が終わるまで待ってください。シミュレータ側では、建機が実際に動き、地形が削られて土が積まれていく様子を確認できます。 **Total Score** を開始前にオンにしておけば、スコアも表示されます。

**8. 停止と再実行**

安全な停止の順番は、 :doc:`simulator-operation` の「安全な停止」に従います。要点は次のとおりです。

1. 自律側を止めます（タスクマネージャのターミナルで ``Ctrl+C`` ）。
2. endpoint と物理シミュレーションが動いている間に、制御している **すべての機体** の ``/<機体名>/emg_stop_cmd`` に ``true`` を publish します（機体名は、 ``ros2 topic list`` で確認した実際の名前です）。
3. Unity を終了します（Play を止めるか、プレイヤーを閉じます）。
4. endpoint のターミナルでも ``Ctrl+C`` を押します。コンテナも止める場合は、ホスト側で ``docker stop opera-hackathon-sample`` を実行します。

再実行するときは、手順を最初から繰り返すだけでなく、各部分の状態をリセットしてください。

- ホスト側でコンテナの状態を確認します。rocker の終了のしかたによって、コンテナが残る場合と消える場合があります。

  .. code-block:: bash

     docker ps -a --filter name=opera-hackathon-sample

  ``opera-hackathon-sample`` という名前のコンテナが一覧にあれば、 ``docker start opera-hackathon-sample`` で起動してから、 ``./enter.sh`` で入ります。一覧になければ、手順 1 の ``./start.sh`` で起動し直します。
- Unity 側は、シーンを開き直すか、Load や Reset で初期状態に戻します。
- ROS 側は、タスクマネージャと endpoint を起動し直します（Reset は ROS のタスクの状態をリセットしないため、ミドルウェア側も立ち上げ直す必要があります）。

正常時のログとトピックの目安
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 3 5

   * - 確認する対象
     - 正常なときの状態
   * - endpoint のログ
     - ``RegisterPublisher`` や ``RegisterSubscriber`` で、 ``/<機体名>/...`` のトピックの登録が OK と表示される
   * - ``ros2 topic list``
     - ``/zx200`` と ``/ic120_0`` の名前空間に、指令用と状態用のトピックが表示される
   * - ``ros2 topic hz /zx200/joint_states``
     - シミュレーション中、メッセージが一定の間隔で流れてくる
   * - タスクマネージャのログ
     - 掘削、運搬、排土の各ステップの進行に対応する出力が出る
   * - Unity のログ
     - ``Physics Start!`` が出ている。 ``Queue full!`` が頻繁に出る場合は、送信キューが詰まっている可能性がある（ :doc:`troubleshooting` を参照）

つまずきやすい点
------------------

- **endpoint は起動したのに、Windows から接続できない**：Linux 側の IP アドレスの指定ミス、ファイアウォール、endpoint が起動していない、の順に確認します。 ``ros2 topic list`` にトピックが表示されていても、それは ROS 側の登録を示すだけで、Windows との通信が成立している証拠にはなりません。
- **トピックは見えるのに、建機が動かない**：Unity 側で ``Physics Start!`` が出ているか、Sim Speed の設定、非常停止の状態（ ``/<機体名>/emg_stop_cmd`` ）を確認します。
- **ic120 が最初から動かない**：タスクの順番上、先に zx200 が掘削を行います。数分待ってから判断してください。

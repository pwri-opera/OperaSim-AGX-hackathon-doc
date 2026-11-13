============================================================
Linux 側ミドルウェア：ROS 2 環境の構築と起動
============================================================

この章では、Ubuntu 22.04 に ROS 2 Humble を直接インストールし、ホスト上のワークスペースでミドルウェアをビルドして起動します。以降のコマンドは Linux PC の Bash で実行します。

一連の動きを手軽にテストしたい場合は、Docker を使う :doc:`sample-run` を参照してください。

ROS 2 と開発ツールの準備
--------------------------

Ubuntu 22.04 を用意し、 `ROS 2 Humble の Ubuntu 向けインストール手順 <https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html>`_ に従って apt リポジトリを設定し、 ``ros-humble-desktop`` をインストールしてください。

続いて開発ツールと依存パッケージをインストールします。以下のパッケージ構成と後述するリポジトリ・ブランチ、ビルド対象は、このリポジトリの ``docker-hackathon-sample/Dockerfile`` をもとにしています。

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y \
     git python-is-python3 python3-colcon-common-extensions python3-rosdep2 \
     ros-humble-rosbridge-suite ros-humble-tf-transformations \
     ros-humble-navigation2 ros-humble-nav2-bringup \
     ros-humble-robot-localization ros-humble-joint-state-publisher \
     ros-humble-joint-trajectory-controller ros-humble-joint-state-broadcaster \
     ros-humble-controller-manager ros-humble-moveit \
     ros-humble-moveit-planners-ompl ros-humble-moveit-planners-chomp \
     ros-humble-moveit-visual-tools ros-humble-diagnostic-updater libboost-all-dev
   source /opt/ros/humble/setup.bash

ワークスペースの作成とビルド
------------------------------

ワークスペースは ``$HOME/opera-ws`` とします。すでにクローンしたリポジトリがある場合は、重複してクローンせず、ブランチを確認してください。

.. code-block:: bash

   mkdir -p "$HOME/opera-ws/src"
   cd "$HOME/opera-ws/src"

   git clone -b main-ros2 https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git
   git clone -b feature/tmp_ic120_unity_setting https://github.com/pwri-opera/ic120_ros2.git
   git clone -b main https://github.com/Ryoya1012/Opera-sim_hackathon-Sample.git
   git clone -b hackathon https://github.com/Ryoya1012/ZX200_autonomy_state_machine.git
   git clone -b main https://github.com/Ryoya1012/Opera-sim_ic120_hackathon.git
   git clone -b main https://github.com/pwri-opera/com3_ros.git
   git clone -b main https://github.com/pwri-opera/gnss_localizer_ros2.git


サンプルの経路データをワークスペース直下にコピーします。このリポジトリをまだ取得していない場合は、先にクローンしてください。

.. code-block:: bash

   git clone https://github.com/pwri-opera/OperaSim-AGX.git "$HOME/OperaSim-AGX"
   cp "$HOME/OperaSim-AGX/docker-hackathon-sample/waypoints.csv" "$HOME/opera-ws/waypoints.csv"

``rosdep`` が未初期化の場合だけ、 ``sudo rosdep init`` を実行します。その後、依存関係を解決してビルドします。

.. code-block:: bash

   cd "$HOME/opera-ws"
   source /opt/ros/humble/setup.bash
   rosdep update
   rosdep install --from-paths src --ignore-src --rosdistro humble -r -y
   colcon build --symlink-install \
     --packages-up-to \
       ic120_navigation task_manager zx200_autonomy ic120_autonomy \
       ic120_unity com3_msgs ros_tcp_endpoint
   source "$HOME/opera-ws/install/setup.bash"

``com3_msgs`` は建機固有のメッセージ型です。endpoint だけでなく、このパッケージもビルドし、ROS コマンドを使うすべてのターミナルでワークスペースの環境を読み込んでください。

endpoint と自律制御の起動
--------------------------

**ターミナル 1：ROS-TCP endpoint**

.. code-block:: bash

   cd "$HOME/opera-ws"
   source /opt/ros/humble/setup.bash
   source "$HOME/opera-ws/install/setup.bash"
   ros2 launch ros_tcp_endpoint endpoint.py

endpoint は ``ROS_IP=0.0.0.0`` 、 ``ROS_TCP_PORT=10000`` で待ち受けます。Windows 側には、この Linux PC の LAN 側 IP アドレスを設定してください。

Windows 側で ROS 接続を行い、Sim Speed を x1.0 にして Start Simulation を押します（ :doc:`simulator-operation` ）。Linux 側の別のターミナルでも上記の 2 つの setup ファイルを読み込み、 ``ros2 topic echo /ic120_0/joint_states --once`` などでフィードバックを確認します。機体名は、実際のトピック一覧に合わせてください。

**ターミナル 2：ハッカソンのサンプル**

接続とフィードバックを確認してから起動します。

.. code-block:: bash

   cd "$HOME/opera-ws"
   source /opt/ros/humble/setup.bash
   source "$HOME/opera-ws/install/setup.bash"
   ros2 launch task_manager hackathon_sample.launch.py

zx200 が掘削・積み込みを行い、そのあと ic120 が運搬・排土・帰還を行います。Docker での通し実行と進行の確認方法は :doc:`sample-run` 、コードの編集と再ビルドは :doc:`development` を参照してください。

ホスト上と Docker の endpoint を同時に起動すると、TCP 10000 番ポートが競合します。切り替えるときは、先に起動中の endpoint を ``Ctrl+C`` で停止してください。

IP アドレスとファイアウォールの確認
-------------------------------------

ここで使う確認コマンドは、Linux PC のシェルで実行します。

endpoint が待ち受けているかを確認します（ホスト側）。

.. code-block:: bash

   ss -tln | grep 10000

Linux 側の IP アドレスを確認します（ホスト側）。

.. code-block:: bash

   ip -4 addr show | grep inet
   # または
   hostname -I

NIC が複数ある場合は、 **Windows PC と同じ LAN につながっている側の IPv4 アドレス** を選びます。 ``127.0.0.1`` 、 ``docker0`` などのブリッジ、VPN 側のアドレスが正しいとは限りません。Windows 側に出るときの経路は、次のコマンドで確認できます（例として、Windows 側の IP アドレスを ``192.168.10.20`` とします）。

.. code-block:: bash

   ip -4 route get 192.168.10.20
   # 出力の src= が使うべき自分のアドレス、dev= が使う NIC です

最終的な確認は、Windows 側の PowerShell から行います。

.. code-block:: powershell

   $LinuxIp = "192.168.10.10"   # 例です。実際の Linux 側の IP アドレスに置き換えてください
   Test-NetConnection -ComputerName $LinuxIp -Port 10000

``TcpTestSucceeded : True`` と表示されれば、endpoint まで届いています。False の場合は、Linux 側のファイアウォールと endpoint の起動状態を確認してください。UFW が有効な場合も、ポートを全体に開放する ``sudo ufw allow 10000/tcp`` は使わず、Windows 側の IP アドレスだけを許可します。

.. code-block:: bash

   sudo ufw status    # UFW が有効かどうかを確認します
   # 例：Windows 側 PC の IP アドレスが 192.168.10.20 の場合
   sudo ufw allow from 192.168.10.20 to any port 10000 proto tcp

``192.168.10.20`` は例です。実際の Windows 側の IP アドレスに置き換えてください。ファイアウォール自体を ``sudo ufw enable`` や ``sudo ufw disable`` で切り替えるのは避けてください。運営のネットワークポリシーがある場合は、そちらに従います。

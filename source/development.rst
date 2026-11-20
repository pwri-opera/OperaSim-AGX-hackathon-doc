==============================================================
ROS 2 ミドルウェアの開発（ホスト上のワークスペース）
==============================================================

この章では、 :doc:`linux-middleware` で作成した ``$HOME/opera-ws`` を使い、自分の ROS 2 ノードや設定を編集して再ビルドします。ソースは ``src/`` 、ビルド成果物は ``build/`` と ``install/`` 、ログは ``log/`` に保存されます。一連の動きを手軽にテストする Docker 環境は :doc:`sample-run` を参照してください。

サンプルのどこを変更するかを調べるときは、 :doc:`sample-implementation` のパッケージ構成とプログラムの流れを参照してください。

環境の読み込みと再ビルド
--------------------------

新しいターミナルを開くたびに、次の環境を読み込みます。

.. code-block:: bash

   source /opt/ros/humble/setup.bash
   source "$HOME/opera-ws/install/setup.bash"

``$HOME/opera-ws/src`` 以下のコードをエディタで編集します。ビルドするときは新しいターミナルで ROS 2 の環境だけを読み込み、ワークスペース直下で実行します。

.. code-block:: bash

   cd "$HOME/opera-ws"
   source /opt/ros/humble/setup.bash
   colcon build --symlink-install \
     --packages-up-to \
       ic120_navigation task_manager zx200_autonomy ic120_autonomy \
       ic120_unity com3_msgs ros_tcp_endpoint

ビルド後は、ノードを実行するターミナルで ``source "$HOME/opera-ws/install/setup.bash"`` を読み込み直し、ノードを再起動してください。依存パッケージに変更がない場合は、 ``colcon build --symlink-install --packages-select <pkg>`` で対象を絞れます。依存関係を変えた場合やパッケージを追加した場合は、 ``rosdep install --from-paths src --ignore-src --rosdistro humble -r -y`` を実行し、 ``--packages-up-to`` で依存パッケージもビルドします。

サンプルの経路データは ``$HOME/opera-ws/waypoints.csv`` に置き、launch はワークスペース直下から実行します。列は ``id,pos_x,pos_y,pos_z,rot_x,rot_y,rot_z,rot_w,xy_goal_tol,des_lin_vel,state`` です。

例：チーム用の起動ファイルで荷台の保持時間を変える
----------------------------------------------------

サンプルが :ref:`sample-run-checklist` のとおり一巡したら、起動ファイルをコピーして、小さな変更を試せます。ここではシミュレータ上で、IC120 が荷台を上げたまま保持する時間を既定の 5.0 秒から 6.0 秒に変えます。ソース本体やインストール済みのファイルは書き換えません。

1. ROS 2 とワークスペースの環境を読み込んだ端末で、インストール済みの起動ファイルをコピーします。Docker を使う場合も操作は同じですが、コピー先にはホストと共有され、コンテナを作り直しても残るディレクトリを選んでください。運営配布イメージでは指定された作業場所を使います。

   .. code-block:: bash

      team_dir=$(mktemp -d "$HOME/opera-team.XXXXXX")
      cp "$(ros2 pkg prefix --share task_manager)/launch/hackathon_sample.launch.py" \
        "$team_dir/team_sample.launch.py"
      printf '%s\n' "$team_dir/team_sample.launch.py"

2. 表示されたファイルをエディタで開きます。 ``executable = 'dump_release_controller'`` の ``Node`` にある ``parameters`` を、次のように変更します。他のノードの設定は変更しません。

   .. code-block:: python

      parameters=[{'use_sim_time': True, 'wait_seconds': 6.0}]

3. :ref:`simulator-safe-stop` の手順で前回の実行を止め、初期状態に戻します。endpoint を起動し直し、Windows 側の ROS 接続と状態の受信を確認してください。経路 CSV があるワークスペース直下（ホスト版なら ``~/opera-ws`` 、このマニュアルの Docker サンプルなら ``/ws`` ）で、通常の launch の代わりにコピーを起動します。新しい端末を使う場合は、ROS 2 とワークスペースの環境を読み込み、下の引数を手順 1 で表示されたファイルの絶対パスに置き換えてください。起動ファイルの変更だけなので、再ビルドは不要です。

   .. code-block:: bash

      ros2 launch "$team_dir/team_sample.launch.py"

4. 同じ ROS 2 環境の別端末で ``ros2 param get /dump_release_controller wait_seconds`` を実行し、値が ``6.0`` になっていることを確認します。シミュレータで排土と帰還まで進み、タスクマネージャに完了ログが出ることも確認します。
5. 元に戻すときは、安全に停止して初期状態に戻し、通常の ``ros2 launch task_manager hackathon_sample.launch.py`` で起動します。同じコマンドで ``wait_seconds`` が元の値（参照した版では ``5.0`` ）に戻ったことを確認してください。変更をチームで使う場合は、コピーした起動ファイルをチームのリポジトリで管理します。

トピックとメッセージの確認
----------------------------

Linux PC のターミナルで、環境を読み込んでから実行します。

.. code-block:: bash

   ros2 topic list | sort
   ros2 topic info /zx200/joint_states
   ros2 topic echo /ic120_0/joint_states --once

``ros2 topic hz`` は、値を出し続けます。確認できたら ``Ctrl+C`` で止めてください。

.. code-block:: bash

   ros2 topic hz /zx200/odom_pose    # Ctrl+C で終了します

建機の名前空間は GameObject 名から決まるため、シーンやセーブデータによって変わることがあります。必ず ``ros2 topic list`` で、実際の名前を確認してください。代表的なトピックは、次のとおりです。

- ``/zx200/joint_states`` 、 ``/ic120_0/joint_states`` （ ``sensor_msgs/msg/JointState`` ）。ブルドーザだけは、 ``/joint_state`` と単数形になる実装の違いがあります。
- ``/zx200/odom_pose`` 、 ``/zx200/global_pose`` （ ``nav_msgs/msg/Odometry`` ）
- ``/clock`` （シミュレーション時計。後述します）

指令用のトピックには、 ``front_cmd`` 、 ``track_cmd`` 、 ``cmd_vel`` 、 ``rot_dump_cmd`` 、 ``track_volume_cmd`` 、 ``blade_cmd`` などがあります。機体と制御モードごとの対応は、 `OperaSim-AGX 本体の README にある対応表 <https://github.com/pwri-opera/OperaSim-AGX/blob/hackathon/README.md#指令値の設定>`_ を参照してください。実際のトピック名とメッセージ型は、この章の確認コマンドで調べてください。

フィードバックを読むだけのノードの例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

指令は送らずに、建機の状態だけを確認したい場合の最小限の例として、 ``joint_feedback.py`` をワークスペースの直下に置きます。保存先は ``~/opera-ws/joint_feedback.py`` です。

.. code-block:: python

   #!/usr/bin/env python3
   import rclpy
   from rclpy.node import Node
   from sensor_msgs.msg import JointState

   class JointFeedback(Node):
       def __init__(self):
           super().__init__("joint_feedback")
           self._reported = False
           self.create_subscription(
               JointState, "/zx200/joint_states", self._callback, 10
           )

       def _callback(self, msg):
           if self._reported:
               return
           self._reported = True
           self.get_logger().info(
               "joint_states: "
               + ", ".join(
                   f"{name}={pos:.4f}"
                   for name, pos in zip(msg.name, msg.position)
               )
           )

   def main():
       rclpy.init()
       node = JointFeedback()
       try:
           rclpy.spin(node)
       except KeyboardInterrupt:
           pass
       finally:
           node.destroy_node()
           if rclpy.ok():
               rclpy.shutdown()

   if __name__ == "__main__":
       main()

最初の 1 件だけ関節名と角度を表示し、そのあとも購読は続けます（表示を 1 回にしているだけです）。指令を送らない読み取り専用の例なので、自律側の指令とは競合しません。環境を読み込んだ Linux PC のターミナルで、次のように実行します。

.. code-block:: bash

   python3 "$HOME/opera-ws/joint_feedback.py"

シミュレーション時計についての注意
------------------------------------

シミュレータは、 ``/clock`` トピックでシミュレーション時間を publish します。シミュレーションが停止している間は、この時計は進みません。物理計算が実時間に追いつかないときは、実時間に対して遅れます。また、Sim Speed の倍率と、実時間の進み方が一致するとは限りません。ROS ノードをシミュレーション時間に同期させたいときは、 ``use_sim_time`` を有効にして、 ``/clock`` を参照させます。ただし、 ``ros2`` コマンドや自作ノードで ``--ros-args -p use_sim_time:=true`` を付け忘れると、実時間とシミュレーション時間がずれて、挙動が分かりにくくなります。実時間で十分な処理では、シミュレーション時間を使わないほうが単純です。

開発するときの注意点
----------------------

- **機体名とトピック名は固定ではありません。** GameObject 名、プレハブ、セーブデータによって、 ``/zx200`` や ``/ic120_0`` などの名前は変わります。コードに直接書き込まず、起動時に ``ros2 topic list`` で調べるか、設定として外から渡してください。
- **制御モードは、指令の control_type だけでは切り替わりません。** ``com3_msgs/msg/JointCmd`` の ``control_type`` フィールドは、メッセージ上の種別です。どの指令の配列を使うかは、機体側の Movement Control Type と Control Type の設定で決まります。詳しくは `OperaSim-AGX 本体の README「指令値の設定」 <https://github.com/pwri-opera/OperaSim-AGX/blob/hackathon/README.md#指令値の設定>`_ のインスペクタ操作を参照してください。
- **メッセージの型は** ``com3_msgs`` **です。** Unity 側が使うのは、 ``com3_msgs/msg/JointCmd`` や ``com3_msgs/msg/FluidPressureArray`` などです。 ``com3_ros`` リポジトリはメッセージ定義の提供元ですが、トピック上では ``com3_msgs/...`` という型名で流れます。フィールドは、 ``ros2 interface show com3_msgs/msg/JointCmd`` で確認できます。

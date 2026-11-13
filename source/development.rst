==============================================================
ROS 2 ミドルウェアの開発（ホスト上のワークスペース）
==============================================================

この章では、 :doc:`linux-middleware` で作成した ``$HOME/opera-ws`` を使い、自分の ROS 2 ノードや設定を編集して再ビルドします。ソースは ``src/`` 、ビルド成果物は ``build/`` と ``install/`` 、ログは ``log/`` に保存されます。一連の動きを手軽にテストする Docker 環境は :doc:`sample-run` を参照してください。

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

指令用のトピックの末尾には、 ``front_cmd`` 、 ``track_cmd`` 、 ``cmd_vel`` 、 ``rot_dump_cmd`` 、 ``track_volume_cmd`` 、 ``blade_cmd`` 、 ``emg_stop_cmd`` があります。機体によって、使えるトピックは異なります。対応関係は、ルートの README の表を参照してください。

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

非常停止
----------

各建機は、 ``/<機体名>/emg_stop_cmd`` （ ``std_msgs/msg/Bool`` ）を購読していて、 ``true`` を受け取ると制御を無効にします。これは指令を無効にするもので、機械が瞬時に固まるわけではありません。受信側は最後に受け取った値を保持するので、メッセージが届けば、 ``false`` を送るまで制御の無効状態が続きます。ただし、publish が確実に届く保証はありません。送ったあとは、建機が実際に止まったことを確認してください。

.. code-block:: bash

   # 制御の無効化を開始する（制御しているすべての機体の名前空間に送ります）
   ros2 topic pub -1 /zx200/emg_stop_cmd std_msgs/msg/Bool "{data: true}"
   ros2 topic pub -1 /ic120_0/emg_stop_cmd std_msgs/msg/Bool "{data: true}"

   # 解除する（自律ノードを止めてから行ってください）
   ros2 topic pub -1 /zx200/emg_stop_cmd std_msgs/msg/Bool "{data: false}"
   ros2 topic pub -1 /ic120_0/emg_stop_cmd std_msgs/msg/Bool "{data: false}"

機体名は、 ``ros2 topic list`` で確認してください。あわせて、自律ノード自体も止めておくのが確実です。

シミュレーション時計についての注意
------------------------------------

シミュレータは、 ``/clock`` トピックでシミュレーション時間を publish します。シミュレーションが停止している間は、この時計は進みません。物理計算が実時間に追いつかないときは、実時間に対して遅れます。また、Sim Speed の倍率と、実時間の進み方が一致するとは限りません。ROS ノードをシミュレーション時間に同期させたいときは、 ``use_sim_time`` を有効にして、 ``/clock`` を参照させます。ただし、 ``ros2`` コマンドや自作ノードで ``--ros-args -p use_sim_time:=true`` を付け忘れると、実時間とシミュレーション時間がずれて、挙動が分かりにくくなります。実時間で十分な処理では、シミュレーション時間を使わないほうが単純です。

開発するときの注意点
----------------------

- **機体名とトピック名は固定ではありません。** GameObject 名、プレハブ、セーブデータによって、 ``/zx200`` や ``/ic120_0`` などの名前は変わります。コードに直接書き込まず、起動時に ``ros2 topic list`` で調べるか、設定として外から渡してください。
- **制御モードは、指令の control_type だけでは切り替わりません。** ``com3_msgs/msg/JointCmd`` の ``control_type`` フィールドは、メッセージ上の種別です。実際にどの指令の配列が使われるかは、機体側の Movement Control Type と Control Type の設定で決まります。機体の設定は、Unity のインスペクタで行います（ルートの README の「オプション」を参照してください）。
- **メッセージの型は** ``com3_msgs`` **です。** Unity 側が使うのは、 ``com3_msgs/msg/JointCmd`` や ``com3_msgs/msg/FluidPressureArray`` などです。 ``com3_ros`` リポジトリはメッセージ定義の提供元ですが、トピック上では ``com3_msgs/...`` という型名で流れます。フィールドは、 ``ros2 interface show com3_msgs/msg/JointCmd`` で確認できます。

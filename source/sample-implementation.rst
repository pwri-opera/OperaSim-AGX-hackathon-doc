============================================================
サンプル実装の構成とプログラムの流れ
============================================================

この章では、ハッカソンのサンプルが、ショベルの掘削・積み込みからクローラダンプの運搬・排土・帰還までをどう実行するか説明します。起動方法は :doc:`linux-middleware` 、Docker で一連の動きを試す手順は :doc:`sample-run` を参照してください。ここで説明するプログラムの役割は、どちらの実行環境でも共通です。

読む順序は、全体を起動する launch、工程を管理する Task Manager、各建機の制御ノードの順がおすすめです。以下は末尾の「確認したソース」に挙げるコミットの実装に基づきます。ブランチは更新されるため、自分の環境のソースも確認してください。

全体の構成
--------------

Task Manager は「何を、どの順番で行うか」を決めます。各建機のノードは、その指示を関節角度や移動目標へ変換し、作業が終わったことを通知します。Unity は指令を受けて物理シミュレーションを進め、関節角度や位置を ROS 側へ返します。

.. code-block:: text

   Linux PC
   Task Manager
     |-- 掘削開始 --> ZX200 状態機械 -- front_cmd --> ROS-TCP endpoint
     |                    |                              ||
     |<-- 掘削・積込完了 --|                              || TCP
     |                                                   ||
     |-- 運搬・帰還 --> IC120 自律走行 --> Nav2             ||
     |                    ^                |              ||
     |                    |-- 移動結果 ----|              ||
     |<-- 到着通知 -------|                |-- cmd_vel -->||
     |                                                   ||
     |-- 荷台上げ・下げ --> 荷台制御 -- rot_dump_cmd ------>||
     |<-- 荷台動作完了 ----|                              ||
                                                         ||
   Windows PC                                            ||
   Unity / AGX <=========================================>>
     |-- joint_states、odom_pose、global_pose、/clock --> ROS 側

これは役割の関係を示した図です。速度指令の実際のトピック名は、launch の remapping で変わります。後述の「名前空間と接続を読むときの注意」も確認してください。

リポジトリとパッケージの対応
--------------------------------

リポジトリ名と ROS 2 パッケージ名は一致しないものがあります。たとえば ``ros2 launch task_manager ...`` の ``task_manager`` は、 ``Opera-sim_hackathon-Sample`` リポジトリが提供するパッケージです。

.. list-table::
   :header-rows: 1
   :widths: 3 2 5

   * - リポジトリ / ブランチ
     - 主なパッケージ
     - 役割と読む場所
   * - ``Ryoya1012/Opera-sim_hackathon-Sample`` / ``main``
     - ``task_manager``
     - ``launch/hackathon_sample.launch.py`` が全体を起動。 ``task_manager/hackathon_sample_manager_node.py`` が工程を管理し、 ``dump_release_controller.py`` が荷台を制御します。
   * - ``Ryoya1012/ZX200_autonomy_state_machine`` / ``hackathon``
     - ``zx200_autonomy``
     - ``zx200_autonomy/state_machine_node.py`` が、関節の目標姿勢を順に切り替えて掘削・積み込みを実行します。
   * - ``Ryoya1012/Opera-sim_ic120_hackathon`` / ``main``
     - ``ic120_autonomy``
     - ``ic120_autonomy/ic120_autonomy_node.py`` が経路 CSV を読み、Nav2 に移動目標を送って到着を通知します。
   * - ``pwri-opera/ic120_ros2`` / ``feature/tmp_ic120_unity_setting``
     - ``ic120_unity`` 、 ``ic120_navigation`` など
     - ``ic120_unity/launch/ic120_standby_ekf.launch.py`` が、Nav2、地図、EKF、TF、ロボットモデルの配信などを立ち上げます。
   * - ``Unity-Technologies/ROS-TCP-Endpoint`` / ``main-ros2``
     - ``ros_tcp_endpoint``
     - Unity と ROS 2 のメッセージを中継します。全体の launch とは別のターミナルで起動します。
   * - ``pwri-opera/com3_ros`` / ``main``
     - ``com3_msgs``
     - 建機の関節指令に使う ``JointCmd`` などのメッセージ型を提供します。

セットアップでは、このほかに ``gnss_localizer_ros2`` も取得します。ただし、今回確認した ``hackathon_sample.launch.py`` から直接起動するノードと、ワークスペースに取得・ビルドするパッケージは、同じ範囲ではありません。

起動から最初の指示まで
--------------------------

``ros2 launch task_manager hackathon_sample.launch.py`` を実行すると、次の起動処理が組まれます。

1. ``ic120_standby_ekf.launch.py`` を読み込み、IC120 のナビゲーション基盤を起動します。既定の機体名は ``ic120_0`` です。
2. ZX200 の ``state_machine_node`` を遅延なしで起動します。
3. launch 開始から 5 秒後に、 ``ic120_autonomy_node`` と ``hackathon_sample_manager_node`` を起動します。
4. launch 開始から 10 秒後に、 ``dump_release_controller`` を起動します。

この秒数は launch の ``TimerAction`` に指定された起動遅延であり、ノードが準備できたことを検出する仕組みではありません。各制御ノードには ``use_sim_time=True`` が渡されるため、起動後の制御タイマーや動作中の待ち時間には Unity の ``/clock`` が関係します。

Task Manager のコンストラクタは publisher と subscriber を作り、状態を ``INIT`` に設定します。 ``start_sequence()`` を呼ぶ 1 秒周期のタイマーは、 ``/start_dig`` の subscriber が見つかるまで待ち、見つかると ``true`` を一度送って自身を停止します。これは ROS 側の受信ノードの確認なので、Unity との接続や関節フィードバックまで確認するわけではありません。起動前の疎通確認が必要なのは、このためです。

Task Manager が進める工程
----------------------------

``TaskManagerNode`` は、完了通知を受けるたびに次の指示を送ります。下表のトピックはすべて ``std_msgs/msg/Bool`` で、 ``true`` が開始または完了の合図です。

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 待機している状態
     - 受け取る通知
     - 次に送る指示 / 遷移先
   * - ``INIT``
     - ``/start_dig`` の subscriber を検出
     - ``/start_dig`` を送信し、 ``WAITING_ZX200_DIG`` へ
   * - ``WAITING_ZX200_DIG``
     - ``/end_dig``
     - ``/ic120/start_transport`` を送信し、 ``WAITING_IC120_TRANSPORT`` へ
   * - ``WAITING_IC120_TRANSPORT``
     - ``/ic120/arrived_dump``
     - ``/ic120/tilt_up_cmd`` を送信し、 ``WAITING_IC120_DUMP`` へ
   * - ``WAITING_IC120_DUMP``
     - ``/ic120/dump_completed``
     - ``/ic120/tilt_down_cmd`` を送信し、 ``WAITING_IC120_TILT_DOWN`` へ
   * - ``WAITING_IC120_TILT_DOWN``
     - ``/ic120/tilt_down_completed``
     - ``/ic120/start_return`` を送信し、 ``WAITING_IC120_RETURN`` へ
   * - ``WAITING_IC120_RETURN``
     - ``/ic120/arrived_home``
     - ``COMPLETE`` へ。全工程の完了をログに出します。

コールバックは、通知が ``true`` か、現在の状態が期待する工程かを調べます。たとえば運搬前に ``arrived_dump`` が届いても、荷台上げには進みません。 ``COMPLETE`` から自動で ``INIT`` へ戻る処理はなく、サンプルは一巡で完了します。また、完了通知が来なかった場合の全体タイムアウトや復旧処理は、この Task Manager には実装されていません。

ZX200：目標姿勢を順に実行する
--------------------------------

``ZX200StateMachine`` は ``/start_dig`` を受けると、次の順に状態を切り替えます。

.. code-block:: text

   IDLE -> REACH -> DIG -> DRAG -> LIFT -> SWING_TO_RELEASE
        -> RELEASE_1 -> RELEASE_2 -> RETURN_1 -> RETURN_2 -> FINISH

``target_angles`` に各状態の目標角度があり、配列の順序は ``joint_names`` の ``swing_joint, boom_joint, arm_joint, bucket_joint`` と対応します。 ``transition_to()`` は前の指令値と次の目標値から動作時間を計算し、 ``timer_callback()`` は 0.1 秒周期で S 字状に補間した位置指令を ``/zx200/front_cmd`` へ送ります。

状態の切り替えには実際のフィードバックを使います。 ``joint_state_callback()`` が ``/zx200/joint_states`` を関節名で読み取り、 ``is_target_reached()`` が全関節について目標との差を確認します。既定では誤差 0.1 rad 以内に入り、その状態で 1 秒待つと次へ進みます。指令の補間時間が経過しただけでは、次の姿勢に進みません。

確認した実装では ``max_dig_count=1`` です。 ``FINISH`` まで到達したあとに ``/end_dig=true`` を送り、Task Manager がダンプの運搬を開始します。トピック名は「掘削完了」ですが、その時点ではショベルの旋回・積み込み・戻り姿勢までのシーケンスが完了しています。 ``/start_release`` の受信処理もありますが、この Task Manager はそれを使わず、 ``LIFT`` から積み込み動作へ自動で進みます。

IC120：経路 CSV と Nav2 の連携
--------------------------------

``IC120AutonomyNode`` は、起動時に ``filename`` パラメータの CSV を読みます。既定は ``waypoints.csv`` で、まず指定パス、次に ``~/ros2_ws/`` 以下を探します。本マニュアルの ``~/opera-ws`` は既定の探索先に含まれないため、ワークスペース直下から launch するか、 ``filename`` に絶対パスを渡してください。

CSV の位置と姿勢は移動目標、 ``state`` はその地点で行う処理を表します。

.. list-table::
   :header-rows: 1
   :widths: 1 2 5

   * - ``state``
     - 地点の役割
     - 到着後の処理
   * - ``0``
     - 通過地点
     - 次の waypoint へ進みます。条件を満たせば到着前に次の goal を送ります。
   * - ``1``
     - 排土場所
     - ``/ic120/arrived_dump`` を通知し、Task Manager の荷台操作指示を待ちます。
   * - ``2``
     - ホーム・積込場所
     - ``/ic120/arrived_home`` を通知し、index と許可フラグを初期化します。

``/ic120/start_transport`` を受けると搬送を許可し、先頭がホームとして使われる構成では index 1 から走行を開始します。 ``_on_timer()`` が ``_send_goal()`` を呼び、CSV の姿勢を ``map`` フレームの ``NavigateToPose.Goal`` にして、Nav2 の ``/ic120_0/navigate_to_pose`` へ非同期で送ります。この Action 名はサンプルの launch が指定しています。

Nav2 が goal を受理すると、結果を受け取るコールバックを登録します。 ``_get_result_callback()`` が結果を保存し、制御タイマーから ``_handle_goal_result()`` を呼んで次の工程へ進めます。通過地点では ``_maybe_preempt_to_next_waypoint()`` による先行切り替えもあり、既定の ``switch_distance`` は 2 m です。この判定には ``odom_topic`` の現在位置が必要です。

排土場所では goal の成功を確認して停止工程へ進みます。荷台上げ・下げの指示を受けたとき、このノードは内部状態だけを更新し、実際の荷台制御は次節のノードに任せます。荷台下降が完了し、 ``/ic120/start_return`` を受けると CSV の次の地点から帰路を進みます。往路を自動で逆順に走る実装ではないので、CSV には帰路とホームの地点も必要です。

``xy_goal_tol`` と ``des_lin_vel`` も CSV から読み込まれますが、確認した実装の ``_send_goal()`` はそれらを Nav2 の許容誤差や速度設定へ反映していません。走行の調整では、CSV だけでなく ``ic120_navigation/params/navigation_parameters_sim.yaml`` と launch のパラメータ設定を確認してください。排土場所やホームへの移動が失敗すると、完了通知を出さずに待機へ戻るため、Task Manager 側は通知待ちのままになります。

荷台制御：実関節位置で完了を判定する
----------------------------------------

``task_manager`` パッケージ内の ``ReleaseController`` は、走行とは独立して荷台を制御します。既定の状態遷移は次のとおりです。

.. code-block:: text

   IDLE -- tilt_up_cmd --> PRE_WAIT -> RAISING -> RAISED_WAIT
        -> WAITING_DOWN_COMMAND -- tilt_down_cmd --> LOWERING -> IDLE

上昇指令を受けると既定で 2 秒待ち、 ``/ic120_0/rot_dump_cmd`` へ ``dump_joint`` の位置指令を送ります。0.1 秒ごとに指令値を 0.02 ずつ変化させ、上昇目標は 1.0、下降目標は 0.0 です。これらはパラメータで変更できます。

``/ic120_0/joint_states`` の実関節位置が上昇目標の許容差 0.1 以内になると、上げた姿勢で既定 5 秒保持して ``/ic120/dump_completed`` を通知します。この通知は荷台位置と保持時間に基づき、土砂がすべて落ちたことをセンサで検出しているわけではありません。

下降指令を受けたあとも実関節位置を確認し、下降目標に達してから ``/ic120/tilt_down_completed`` を送ります。フィードバックが来なければ、指令値だけが目標に達しても完了にはなりません。

名前空間と接続を読むときの注意
----------------------------------

``/ic120/start_transport`` などの ``/ic120`` は、Task Manager と制御ノード間で使う作業指示の名前空間です。一方、 ``/ic120_0/joint_states`` などの ``/ic120_0`` は、Unity 内の機体に対応します。機体を増やしたり名前を変えたりするときは、作業指示・機体通信・Nav2 Action・TF の設定をそれぞれ確認する必要があります。

また、ソース内に書かれたトピック名と、launch 後の接続先は同じとは限りません。確認したコードには、次の接続上の注意点があります。

- ``ic120_autonomy_node`` の ``cb_bridge_cmd_vel()`` は、ソース上では ``/cmd_vel`` を受けて ``/ic120_0/cmd_vel`` へ転送します。しかしサンプルの launch は後者を ``/cmd_vel`` へ remap するため、このノードの受信先と送信先が同じになります。単純な一方向の中継として扱わず、実行時の publisher / subscriber を確認してください。
- 同じ launch は ``/ic120_0/track_cmd`` を ``/ic120_0track_cmd`` へ remap します。後者には機体名の後の ``/`` がありません。また、確認した自律走行コードには ``publish_track_command()`` の定義はありますが、その呼び出しはありません。関数があることだけで、履帯指令が送られているとは判断できません。
- 自律走行ノードの ``odom_topic`` の既定は ``/ic120_0/odom`` です。一方、ナビゲーション基盤は ``odom_pose`` を使う設定を持ち、EKF の出力は ``/ic120_0/odometry/global`` です。先行 goal 切り替えに必要な現在位置が、自律走行ノードへ届いているかを確認してください。

ホスト上のワークスペースの環境を読み込んだターミナルで、実際の接続を調べられます。

.. code-block:: bash

   ros2 node info /ic120_autonomy_node
   ros2 topic info /cmd_vel --verbose
   ros2 topic info /ic120_0/cmd_vel --verbose
   ros2 topic info /ic120_0/odom --verbose
   ros2 action list -t

これらはソース上の接続設定を説明したもので、実行環境での動作検証結果ではありません。独自の relay や remapping を追加するときも、同じ速度指令を複数経路で送らないかを確認してください。

改造するときの入口
----------------------

- **工程を変える**： ``hackathon_sample_manager_node.py`` の ``TaskState`` とコールバックを変更します。指示を受ける側の状態遷移と完了通知も合わせます。
- **掘削姿勢を変える**： ``state_machine_node.py`` の ``target_angles`` 、 ``max_speeds`` 、 ``max_dig_count`` を確認します。目標姿勢はシーン内の地形や積込位置に依存します。
- **運搬経路を変える**： ``waypoints.csv`` の位置・姿勢・ ``state`` を編集します。Nav2 の走行特性はナビゲーションの YAML と launch も確認します。
- **荷台動作を変える**： ``dump_release_controller`` の ``raised_position`` 、 ``lowered_position`` 、 ``pre_wait_seconds`` 、 ``wait_seconds`` などを調整します。

コードを編集して再ビルドする方法と、フィードバックを読む小さなノードの例は :doc:`development` を参照してください。

確認したソース
------------------

以下の固定コミットを確認しました。実装を追うときは、各リンクのファイル名と、この章で挙げた関数名を手掛かりにしてください。

- `全体起動の launch <https://github.com/Ryoya1012/Opera-sim_hackathon-Sample/blob/e907d5604c686ecd6e7c2aa9f2c94d1d943f4ab6/launch/hackathon_sample.launch.py>`_
- `Task Manager <https://github.com/Ryoya1012/Opera-sim_hackathon-Sample/blob/e907d5604c686ecd6e7c2aa9f2c94d1d943f4ab6/task_manager/hackathon_sample_manager_node.py>`_
- `荷台制御 <https://github.com/Ryoya1012/Opera-sim_hackathon-Sample/blob/e907d5604c686ecd6e7c2aa9f2c94d1d943f4ab6/task_manager/dump_release_controller.py>`_
- `ZX200 の状態機械 <https://github.com/Ryoya1012/ZX200_autonomy_state_machine/blob/092f08f37139d8297d292321e53f7f955e9f5cc9/zx200_autonomy/state_machine_node.py>`_
- `IC120 の自律走行 <https://github.com/Ryoya1012/Opera-sim_ic120_hackathon/blob/12a01c2a728d0780deb5155d5344e5b4b6c6cca9/ic120_autonomy/ic120_autonomy_node.py>`_
- `IC120 のナビゲーション基盤 <https://github.com/pwri-opera/ic120_ros2/blob/a27ad3e8084e2f2fa32ff6442db49b0e202e1a66/ic120_unity/launch/ic120_standby_ekf.launch.py>`_

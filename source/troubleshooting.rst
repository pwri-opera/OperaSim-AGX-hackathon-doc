========================
トラブルシューティング
========================

症状ごとに、確認するポイントと対処をまとめています。まず、「シミュレータが起動するか」と「endpoint が待ち受けているか」の 2 点を切り分けると、原因を絞りやすくなります。

ライセンス
------------

会場の認証済み PC でライセンスエラーが出た場合は、再認証せず運営に連絡してください。下の確認手順は、自分の PC で事前検証する場合に使います。

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - エディタやプレイヤーの起動時に、AGX のライセンスエラーが出る
     - License Manager で、ライセンスの情報（有効期限、モジュール）を確認する
     - ``.lfx`` または ``.lic`` が、実行ファイルがあるフォルダ（カレントディレクトリ）の下にあるかを確認します。エディタの場合は、 ``Assets/AGXUnity/Plugins/x86_64`` に置かれているかを確認します。
   * - 別の PC にコピーしたライセンスが使えない
     - ``agx.lfx`` は、アクティベーションした PC のハードウェアに紐付いている
     - PC ごとに、それぞれアクティベーションします。ファイルをコピーしても使えません。

バージョンと DLL
------------------

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - Unity でプロジェクトを開けない、またはパッケージのエラーが出る
     - Unity のバージョンが 2022.3.62f3 かどうか
     - Unity Hub で正しいバージョンを指定して、開き直します。AGXUnity や ros-tcp-connector は、更新したり差し替えたりしないでください。
   * - プレイヤーを起動すると、DLL が足りないというエラーで終了する
     - 配布物に ``<名前>_Data\Plugins\x86_64`` が一式そろっているか。 ``MSVCP140.dll`` や ``VCRUNTIME140.dll`` が足りないというエラーなら、Visual C++ 再頒布可能パッケージが原因であることが多い
     - 配布物を入手し直します。足りないファイルだけを手動で補うのはやめてください。Visual C++ のファイルが足りない場合は、公式の最新サポート対象の再頒布可能パッケージ（x64）をインストールします： `Microsoft Learn - Latest supported Visual C++ Redistributable downloads <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist>`_
   * - AGX の初期化時に、モジュールが足りないというエラーが出る
     - License Manager のモジュール一覧に、Core、Particles、Granular、Terrain、Tracks がそろっているか
     - ベンダーに、モジュール構成を確認します。

ROS 接続と環境
----------------

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - Windows から endpoint に接続できない
     - Linux ホストで endpoint が TCP 10000 番ポートを待ち受けているか、Windows からそのポートに接続できるか
     - まず Linux 側で待ち受けを確認します。待ち受けているのに Windows から接続できない場合は、接続先 IP アドレスとファイアウォールを確認します。 ``0.0.0.0`` は接続先に使えません。コマンドと結果の見方は :ref:`check-ros-tcp-connection` を参照してください。
   * - 配布バイナリで HUD の IP アドレス入力欄を操作できない
     - 自動接続設定が有効か。接続処理中（ ``HasConnectionThread`` が ``true`` の間）は入力欄が無効になります
     - 運営に **Connect On Start** が無効で **Show HUD** が有効なビルドを依頼するか、自分でビルドします（ :doc:`windows-setup` を参照）。
   * - ``ros2 topic`` が ``com3_msgs`` 関連のエラーになる
     - ``com3_msgs`` をビルド済みか、ワークスペースの環境を読み込んでいるか
     - コマンドを実行するターミナルで、 ``source /opt/ros/humble/setup.bash`` と ``source "$HOME/opera-ws/install/setup.bash"`` を実行します。Docker のテストでは、同じコンテナ内で ``source /ws/install/setup.bash`` を実行します。
   * - ``Unknown message class`` が大量に出る
     - ``com3_msgs`` を知らない環境で、endpoint が動いている
     - :doc:`linux-middleware` に従って ``com3_msgs`` をビルドし、その環境を読み込んで endpoint を再起動します。

シミュレータの動作
--------------------

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - 建機がまったく動かない
     - Unity のログ（またはプレイヤーの ``Player.log`` ）に ``Physics Start!`` があるか（ ``ActionMode=3`` になっているか）。Start Simulation を押したか。Sim Speed の設定
     - Start Simulation を押し直します。 ``Physics Start!`` が出ていなければ、物理シミュレーションが始まっていないので、シーンの状態を確認します。
   * - 建機は動くが、指令に反応しない
     - ``/<機体名>/emg_stop_cmd`` に ``true`` が残っていないか
     - ``ros2 topic pub -1 /<機体名>/emg_stop_cmd std_msgs/msg/Bool "{data: false}"`` で解除できます。ただし、解除したり自律制御を再開したりする前に、指令を publish するノードがすべて止まっていることを確認してください。自律ノードが動いたまま解除すると、指令が再開してしまいます。
   * - ``Queue full!`` が頻繁に出る
     - 送信キューが詰まっている（既知の問題です。パブリッシャには ``extendSendQueue`` の切り替えが用意されています）
     - フィードバックの遅れや、指令が届かない現象として現れることがあります。Sim Speed を x1.0 に戻し、endpoint 側の負荷とメッセージのエラーを確認してください。Unity の ``Player.log`` または ``Editor.log`` と、endpoint のログを記録して、運営または開発者に相談してください。頻度や影響は環境によって異なるため、一律の対処法は示せません。
   * - トピック名がドキュメントと違う
     - ``ros2 topic list`` に表示される実際の名前
     - 機体名は GameObject 名から決まるので、シーンやセーブデータによって変わります。また、 ``/joint_states`` と ``/joint_state`` のように、機体ごとの実装の違いもあります。一覧で確認してから使ってください。

GUI と Docker（sample-run を使う場合）
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - コンテナ内で GUI が表示されない
     - ``./start.sh`` （rocker の ``--x11`` ）で起動したか。 ``echo $DISPLAY`` と X11 の設定
     -  :doc:`sample-run` の手順で rocker 経由で起動し直します。
   * - NVIDIA の GPU を使いたい
     - nvidia-container-toolkit が、ホストにインストールされているか
     - ``./start-nvidia.sh`` を使います。インストールされていない場合は、公式の手順でインストールしてください。
   * - コンテナ内で編集した内容が消えた
     - ``start.sh`` 系のスクリプトは、 ``/ws`` をバインドマウントしていない。コンテナを作り直すと、 ``/ws`` は初期状態に戻る
     - 残したい編集は、 :doc:`linux-middleware` で作るホスト上のワークスペースで行ってください。

パスとデータ
--------------

.. list-table::
   :header-rows: 1
   :widths: 3 4 4

   * - 症状
     - 確認するポイント
     - 対処
   * - セーブしてからロードしても、状態が元に戻らない
     - ``Assets/SaveData/setting`` と ``Assets/SaveData/simulation`` の中身。同名のファイルを上書きしていないか
     - 保存先を確認して、必要ならバックアップから復元します。プレイヤーでは、カレントディレクトリが基準になる点に注意してください。
   * - サンプルが waypoint のファイルを見つけられない
     - ホスト上の ``~/opera-ws/waypoints.csv`` （Docker のテストでは ``/ws/waypoints.csv`` ）があるか
     - ホストではワークスペース直下にファイルを置き、そのディレクトリから launch を実行します。Dockerfile から作ったイメージには ``/ws/waypoints.csv`` がコピーされています。
   * - 設定値が反映されない
     - ``SettingData.json`` は、 ``persistentDataPath`` （ ``%USERPROFILE%\AppData\LocalLow\VMC Motion Technologies\PWRI_KenkiSimulator`` ）に保存される
     - ROS の接続先 IP アドレスは、このファイルを書き換えても変わりません。接続の設定は、プレハブとシーンに保存されている値が使われます。

.. _participant-support:

開催前に解決しないとき
----------------------

事前準備の案内が見つからない、指定環境を用意できない、またはサンプルが完了しない場合は、 `土木研究所の募集要項「問い合わせ先」 <https://www.pwri.go.jp/team/advanced/opera-hackathon-2.html>`_ に掲載されている先端技術チーム（ ``sentan@pwri.go.jp`` ）に連絡してください。参加者向けの案内に別の窓口がある場合は、そちらを使ってください。

動作について問い合わせるときは、次の情報を添えてください。

- Windows・Linux のバージョンと、使用した構成（運営配布イメージ、公開 Docker サンプル、ホスト版のいずれか）。
- シミュレータの配布版または Git コミット、Docker イメージのタグまたはイメージ ID。ソースからビルドした場合は、分かる範囲でサンプル側のコミットも記載します。
- :ref:`sample-run-checklist` で最後に通過した項目、失敗した操作、再現手順、表示されたエラー。
- :doc:`simulator-operation` の「ログの場所」にある Unity の ``Player.log`` または ``Editor.log`` と、Linux 側で endpoint とサンプルを起動した端末の出力。採点の相談では、 :doc:`scoring` にある採点ログも添えます。

ログやスクリーンショットを共有する前に、ライセンスファイル、アクティベーション用のパスワードなどの認証情報が含まれていないことを確認してください。

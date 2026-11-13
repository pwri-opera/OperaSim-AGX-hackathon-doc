==============================================
Windows 側のセットアップ：バイナリ版とソース版
==============================================

Windows PC でシミュレータを動かす方法は、2 つあります。配布されたビルド済みプレイヤーを使う方法と、ソースから Unity プロジェクトをビルドする方法です。どちらを選んでもシミュレータの動作は同じですが、ROS の接続先 IP アドレスを変更できるかどうかに、大きな違いがあります。まず :ref:`windows-ros-ip` を読んでから、どちらの方法にするかを決めてください。

- **ルート A（バイナリ）**：Unity Editor も Unity のライセンスも不要です。配布物を展開して実行するだけです。
- **ルート B（ソース）**：Unity Editor 2022.3.62f3 と、AGX ライセンスのアクティベーションが必要です。自分用の接続設定で、プレイヤーをビルドできます。

.. _windows-ros-ip:

ROS 接続先 IP アドレスを変更できるか（重要）
----------------------------------------------

シミュレータの ROS 接続設定は、 ``Assets/Resources/ROSConnectionPrefab.prefab`` に保存されています。既定値は ``127.0.0.1:10000`` で、 ``ConnectOnStart`` と ``ShowHUD`` は、どちらも有効です。

注意が必要なのは、 **配布バイナリが自動接続モードでビルドされている場合、実行中の HUD から接続先 IP アドレスを変更できない** ことです。接続が始まった後（ ``HasConnectionThread`` が true の間）は、IP アドレスとポートの入力欄が無効になります。レジストリ、 ``SettingData.json`` 、PlayerPrefs を書き換えても、接続先は変わりません（ ``SettingData.RosIP`` は保存されるだけで、接続処理では参照されません）。

そのため、配布バイナリを使う場合は、次のどちらかに当てはまるかを運営に確認してください。

- ビルド時に **Connect On Start が無効、Show HUD が有効** の設定になっている（起動するたびに、HUD で IP アドレスとポートを入力して Connect できます）。
- 接続先の IP アドレスが、会場の Linux 側の IP アドレスに **正しく埋め込まれている** 。

どちらにも当てはまらない場合は、後述のソースビルドで自分用のプレイヤーを作るのが確実です。

ルート A：配布バイナリを使う
------------------------------

運営から配布されたビルド済みプレイヤーを展開します。このルートでは、Unity Editor と Unity のライセンスは不要です。

1. **配布物は、フォルダごと展開します。** Windows の Unity プレイヤーは、実行ファイル単体では動きません。 ``UnityPlayer.dll`` と ``<名前>_Data`` フォルダ一式が必要です。exe だけを別の場所にコピーしないでください。展開後のフォルダ構成は、おおむね次のようになります（名前は例です。配布物によって異なります）。

   .. code-block:: text

      OperaSim-AGX\                 ← 配布フォルダをそのまま展開した例
      ├── OperaSim.exe             ← 実行ファイルの例（配布物によって名前は異なります）
      ├── UnityPlayer.dll
      └── OperaSim_Data\
          ├── Managed\
          └── Plugins\
              └── x86_64\          ← AGX Dynamics のネイティブ DLL とランタイムデータ

2. AGX のライセンスファイル（ ``.lfx`` または ``.lic`` ）を、実行ファイルがあるフォルダか、その下のフォルダに置きます。詳しくは :doc:`agx-license` を参照してください。プレイヤーはカレントディレクトリから再帰的にライセンスを探すので、エクスプローラーで exe をダブルクリックするのではなく、exe があるフォルダをカレントディレクトリにして起動するのが確実です。
3. ROS の接続先が、上の条件を満たしているかを確認します。満たしていない場合は、ルート B のソースビルドに切り替えてください。
4. 起動すると、セットアップ用の画面が表示されます。操作方法は :doc:`simulator-operation` を参照してください。

PowerShell で、exe があるフォルダに移動してから起動すると確実です（ ``OperaSim.exe`` は、実際の exe 名に置き換えてください）。

.. code-block:: powershell

   Set-Location C:\work\OperaSim-AGX   # exe があるフォルダ
   .\OperaSim.exe

DLL が不足して起動できない場合は、 :doc:`troubleshooting` を参照してください（ ``MSVCP`` や ``VCRUNTIME`` に関するエラーであれば、Visual C++ 再頒布可能パッケージをインストールすると解決することがあります）。

ルート B：ソースからビルドする
--------------------------------

ソースの入手と Unity プロジェクトの起動
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Git for Windows をインストールし、リポジトリをクローンします。パスには、日本語や空白を含まない短い場所を使うことをおすすめします。次の PowerShell の例では、先に ``C:\work`` を作っています。

   .. code-block:: powershell

      New-Item -ItemType Directory -Force C:\work | Out-Null
      git clone https://github.com/pwri-opera/OperaSim-AGX.git C:\work\OperaSim-AGX

   ハッカソンで別の URL が指定されている場合は、そちらを使ってください。
2. Unity Hub をインストールします（公式サイト： `https://unity.com/download <https://unity.com/download>`_ ）。続いて、Unity **2022.3.62f3** をインストールします（ ``ProjectVersion.txt`` で指定されているバージョンです）。Unity Hub の一覧に表示されない場合は、 `Unity Editor Archive <https://unity.com/releases/editor/archive>`_ から 2022.3.62f3 を入手してください。
3. Unity Hub で「Add」→「Add project from disk」を選び、クローンしたフォルダを追加して、2022.3.62f3 で開きます。初回は、パッケージの解決とインポートに時間がかかります。
4. Unity Editor を使うには、Unity のライセンスが必要です。どのプランや契約形態のライセンスを使えるかは、Unity の契約条件に従います。このマニュアルでは、特定のプランが使えるとは案内しません。
5. ``Packages/manifest.json`` にある Git 依存パッケージ（ ``com.unity.robotics.ros-tcp-connector`` と ``com.unity.robotics.urdf-importer`` ）は、自動的に解決されます。バージョンは ``Packages/packages-lock.json`` に固定されているので、更新せずにそのまま使ってください。
6. プロジェクトを開いたら、Project ウィンドウから ``Assets/Scenes/GameScene.unity`` を開きます（ ``EditorBuildSettings`` で有効になっているシーンは、これだけです）。README に出てくる ``MainScene.unity`` は古いシーンなので、使いません。

AGX ライセンスのアクティベーション（エディタ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

エディタで **AGXUnity > License > License Manager** を開きます。

1. **License Id** と **Activation Password** を入力します。
2. **License File Directory** に ``Assets/AGXUnity/Plugins/x86_64`` を指定します。この欄は、プロジェクト内のフォルダを表示するだけのラベルで、直接入力はできません。クリックするとフォルダ選択ダイアログが開くので、そこから選びます。未設定の場合や、存在しないフォルダを指定した場合は、 ``Assets`` 直下に保存されます。このガイドでは、 ``Assets/AGXUnity/Plugins/x86_64`` を保存先とします。
3. **Activate** を押します。生成された ``agx.lfx`` が、指定したフォルダに保存されます。

詳しくは :doc:`agx-license` を参照してください。同じ PC でアクティベーション済みのライセンスは、条件が許せば、エディタとビルド済みプレイヤーの両方で使えます。

ROS 接続先の設定
~~~~~~~~~~~~~~~~~

1. Play モードに入る前に、メニューの **Robotics > ROS Settings** を開きます。
2. Protocol を **ROS2** に、IP アドレスを Linux 側 PC の IP アドレスに、ポートを ``10000`` に設定します。この Protocol の設定は、ビルド時とエディタ上でのものです。実行中のプレイヤーの HUD からは変更できません。
3. **Play モードを抜けた状態で** 、シーンとプレハブの変更を保存します（Ctrl+S）。Play 中に設定を変えても、保存されません。

配布用や再利用用のビルドを作る場合は、さらに ``ROSConnectionPrefab`` の ``Connect On Start`` を無効にし、 ``Show HUD`` は有効のままにします。こうしておくと、起動するたびに HUD で接続先を入力して Connect できます。 ``ROS2`` のスクリプティングシンボルの定義は、変更せずに残してください。

ビルド
~~~~~~

1. **File > Build Settings** を開きます。
2. Platform が Windows になっていることと、シーン一覧で ``GameScene`` にチェックが入っていることを確認します。
3. Player Settings で Company Name と Product Name を確認します（既定値は ``VMC Motion Technologies`` と ``PWRI_KenkiSimulator`` です）。この値によって、Windows の ``%USERPROFILE%\AppData\LocalLow`` 以下にある保存先のパスが決まります。
4. **Build** を押して、出力先を選びます。ターゲットは Windows x86_64、スクリプティングバックエンドは Mono です。IL2CPP への切り替えや、AGXUnity の更新は行わないでください。
5. ビルドしたプレイヤーは、ルート A と同様に、フォルダごと配置します。ライセンスファイルを exe があるフォルダの下に置いてから、起動してください。

ソースビルドが必要になる典型的なケース
----------------------------------------

- 配布バイナリの接続先が、会場の IP アドレスと合っていない
- 自動接続のため HUD の IP アドレス入力欄が無効になっていて、変更できない
- シミュレータ側のコードを自分で改造したい

このような場合は、ルート B で ``Connect On Start`` を無効にしたプレイヤーをビルドするか、Unity Editor の Play で直接使ってください（ :doc:`simulator-operation` を参照）。

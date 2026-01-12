# mytool - CLIの入口を統一する仕組みを学ぶ

学習用のPython CLIツール。サブコマンド形式で複数の機能を1つのコマンドから実行できる。

## 📚 「入口を統一する」とは？

**従来の問題：**
- `hello.py`, `sum.py`, `check.py` のように処理ごとに別々のスクリプトを作ると管理が煩雑
- 各スクリプトで共通オプション（`--verbose`, `--json`など）を重複実装する必要がある
- ユーザーはどのスクリプトがあるか覚えておく必要がある

**入口統一の解決策：**
- **1つのコマンド** `mytool` だけを提供
- **サブコマンド**で機能を切り替える: `mytool hello`, `mytool sum`, `mytool check`
- **共通オプション**を一箇所で実装し、全サブコマンドで利用可能
- **統一されたエラー処理**と終了コードの管理

これはGit (`git commit`, `git push`) やDocker (`docker run`, `docker ps`) などの実務ツールと同じ設計パターンです。

---

## 🚀 セットアップと実行

### 依存関係のインストール

```bash
# uvを使う場合（推奨）
uv sync

# または pip
pip install -e .
```

### 実行方法

#### 方法1: `python -m mytool` で実行（開発中）

```bash
# hello コマンド
uv run python -m mytool hello
uv run python -m mytool hello tsune --upper
uv run python -m mytool hello Alice --json

# sum コマンド
uv run python -m mytool sum 1 2 3
uv run python -m mytool sum 10 20 30 40 --json

# check コマンド
uv run python -m mytool check --mode ok
uv run python -m mytool check --mode fail --verbose
```

#### 方法2: `mytool` コマンドで実行（インストール後）

```bash
# pipでインストール
pip install -e .

# その後、直接実行可能
mytool hello
mytool sum 5 10 15
mytool check --mode ok
```

#### 方法3: uvでエントリポイント実行

```bash
uv run mytool hello
uv run mytool sum 1 2 3 --json
```

---

## 📖 コマンド仕様

### 共通オプション

すべてのサブコマンドで使える共通オプションは、**サブコマンドの前**に指定します。

- `--verbose`, `-v`: 詳細な出力を表示（エラー時はスタックトレースも表示）

**例:**
```bash
# 正しい使い方：共通オプションはサブコマンドの前
mytool --verbose check --mode fail

# 間違った使い方：これはエラーになります
mytool check --mode fail --verbose
```

---

### 1. `mytool hello [NAME]`

挨拶メッセージを表示します。

**引数:**
- `NAME`: 挨拶する相手の名前（省略時は "world"）

**オプション:**
- `--upper`: メッセージを大文字にする
- `--json`: JSON形式で出力
- `--verbose`, `-v`: 詳細な出力（エラー時はスタックトレース表示）

**例:**
```bash
$ mytool hello
Hello, world!

$ mytool hello tsune --upper
HELLO, TSUNE!

$ mytool hello Bob --json
{"message": "Hello, Bob!"}
```

---

### 2. `mytool sum N1 N2 ...`

複数の整数を合計します。

**引数:**
- `N1 N2 ...`: 合計する整数のリスト（1つ以上必須）

**オプション:**
- `--json`: JSON形式で出力
- `--verbose`, `-v`: 詳細な出力

**例:**
```bash
$ mytool sum 1 2 3
合計: 6

$ mytool sum 10 20 30 --json
{"sum": 60, "count": 3}

$ mytool sum
エラー: 少なくとも1つの数値が必要です
（終了コード: 2）
```

---

### 3. `mytool check --mode {ok|fail}`

チェック処理を実行します（成功/失敗のシミュレーション）。

**オプション:**
- `--mode`: チェックモード
  - `ok`: 成功して終了コード0で終了
  - `fail`: 失敗して終了コード1で終了
- `--verbose`, `-v`: 失敗時にスタックトレースを表示

**例:**
```bash
$ mytool check --mode ok
✓ チェック成功

$ mytool check --mode fail
エラー: 意図的な失敗: チェックモードが'fail'に設定されています
（終了コード: 1）

$ mytool check --mode fail --verbose
エラー: 意図的な失敗: チェックモードが'fail'に設定されています

--- スタックトレース ---
Traceback (most recent call last):
  ...
```

---

## 📊 終了コードの一覧

| 終了コード | 意味 | 発生条件 |
|-----------|------|---------|
| **0** | 成功 | 処理が正常に完了した |
| **1** | 失敗 | 処理中にエラーが発生した（例: `check --mode fail`） |
| **2** | 引数エラー | 不正な引数が渡された（例: `sum`を引数なしで実行） |

終了コードは `echo $?`（Linux/Mac）または `echo %ERRORLEVEL%`（Windows）で確認できます。

```bash
$ mytool check --mode ok
✓ チェック成功
$ echo $?
0

$ mytool check --mode fail
エラー: 意図的な失敗...
$ echo $?
1

$ mytool sum
エラー: 少なくとも1つの数値が必要です
$ echo $?
2
```

---

## 🏗️ プロジェクト構成

```
.
├── pyproject.toml          # ★エントリポイント定義（[project.scripts]）
├── README.md
└── mytool/
    ├── __init__.py         # パッケージ初期化
    ├── __main__.py         # ★入口1: `python -m mytool` で実行
    ├── cli.py              # ★入口2: サブコマンドと共通オプション定義
    └── core.py             # ビジネスロジック
```

### 重要なファイルの役割

| ファイル | 役割 |
|---------|------|
| `__main__.py` | `python -m mytool` で実行されるエントリポイント |
| `cli.py` | typerでサブコマンドと共通オプションを定義（**入口の中心**） |
| `core.py` | 実際の処理ロジック（CLIから分離することでテスト容易性向上） |
| `pyproject.toml` | エントリポイント `mytool` を定義（`[project.scripts]`） |

---

## 🎯 学習課題（5問）

実際に手を動かして、CLIツールの設計を深く理解しましょう。

### 課題1: サブコマンドを1つ追加する【基礎】

**内容:**
`mytool greet --lang {en,ja}` という新しいサブコマンドを追加してください。
- `--lang en` なら "Good morning!"
- `--lang ja` なら "おはようございます！"
- `--json` オプションにも対応

**ヒント:**
1. `core.py` に `greet_logic(lang: str) -> str` 関数を追加
2. `cli.py` に `@app.command()` で `greet` コマンドを追加

---

### 課題2: 共通オプション `--quiet` を追加する【中級】

**内容:**
すべてのサブコマンドで使える `--quiet` オプションを追加してください。
- `--quiet` が指定された場合は最小限の出力のみ（例: 数値だけ）
- `--verbose` と `--quiet` が両方指定された場合はエラーを出す

**ヒント:**
1. `cli.py` の `common_options()` 関数に `--quiet` を追加
2. 各サブコマンド内で `ctx.obj["quiet"]` を確認して出力を制御

---

### 課題3: エラーメッセージを色付けする【中級】

**内容:**
エラーメッセージを赤色、成功メッセージを緑色で表示してください。

**ヒント:**
- `rich` ライブラリを使うか、ANSIエスケープシーケンスを使う
- `pyproject.toml` に依存を追加: `rich>=13.0.0`

---

### 課題4: 設定ファイルを読み込む【上級】

**内容:**
`~/.mytool.json` から設定を読み込み、デフォルト値として使えるようにしてください。

例: `~/.mytool.json`
```json
{
  "default_name": "tsune",
  "always_json": true
}
```

**ヒント:**
1. `common_options()` で設定ファイルを読み込む
2. 読み込んだ値を `ctx.obj` に保存
3. 各サブコマンドでデフォルト値として使う

---

### 課題5: `mytool --version` を実装する【上級】

**内容:**
`mytool --version` でバージョン情報を表示できるようにしてください。

**ヒント:**
1. typerの `version_option` を使う
2. `__init__.py` の `__version__` を読み込む
3. または `app = typer.Typer(...)` に `version=...` を追加

---

## 💡 学習ポイントのまとめ

このプロジェクトを通して学べること：

1. **エントリポイントの仕組み**
   - `__main__.py` による `python -m package` 実行
   - `pyproject.toml` の `[project.scripts]` によるコマンド登録

2. **サブコマンドパターン**
   - `typer.Typer()` で統一されたCLIアプリケーションを構築
   - `@app.command()` で複数のサブコマンドを登録

3. **共通オプションの実装**
   - `@app.callback()` で全サブコマンド共通の処理
   - `typer.Context` でコマンド間のデータ共有

4. **終了コードの制御**
   - 成功（0）、失敗（1）、引数エラー（2）の使い分け
   - `sys.exit()` による明示的な終了コード指定

5. **エラーハンドリングのベストプラクティス**
   - 例外の握りつぶし禁止
   - ユーザー向けメッセージ + verbose時の詳細情報
   - 適切な終了コードの返却

---

## 🔗 参考リンク

- [Typer 公式ドキュメント](https://typer.tiangolo.com/)
- [Python パッケージング ユーザーガイド](https://packaging.python.org/)
- [終了コードの慣習](https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html)

---

**Happy Learning! 🎓**

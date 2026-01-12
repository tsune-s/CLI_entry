"""
★ここが「入口統一」の仕組み（その2）：CLIインターフェース

typer.Typer() でアプリケーションを作成し、@app.command() でサブコマンドを登録する。
これにより、`mytool hello`, `mytool sum`, `mytool check` のように
1つのコマンドから複数のサブコマンドを呼び出せる。
"""

import json
import sys
import traceback
from typing import Annotated, Optional

import typer

from mytool.core import check_logic, hello_logic, sum_logic

# ★typer.Typer()でCLIアプリケーションを作成
# これが全サブコマンドの「入口」になる
app = typer.Typer(
    name="mytool",
    help="学習用CLIツール - サブコマンド形式でさまざまな処理を実行",
    add_completion=False,  # シェル補完は無効化（学習用のためシンプルに）
)


# ★共通オプションの定義
# コールバック関数で全サブコマンド実行前に共通オプションを処理できる
@app.callback()
def common_options(
    ctx: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="詳細な出力を表示（エラー時はスタックトレースも表示）",
        ),
    ] = False,
):
    """
    全サブコマンドに共通するオプションを定義

    この関数はどのサブコマンドが実行される前にも呼ばれる。
    ここで設定した値は、コンテキスト経由で各サブコマンドに渡される。
    """
    # typerのコンテキストに共通オプションを保存
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["verbose"] = verbose


# ============================================================
# ★サブコマンド1: hello
# ============================================================
@app.command()
def hello(
    ctx: typer.Context,
    name: Annotated[
        Optional[str],
        typer.Argument(help="挨拶する相手の名前"),
    ] = "world",
    upper: Annotated[
        bool,
        typer.Option("--upper", help="メッセージを大文字にする"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="JSON形式で出力"),
    ] = False,
):
    """
    挨拶メッセージを表示する

    例:
        mytool hello
        mytool hello Alice --upper
        mytool hello Bob --json
    """
    try:
        # core.pyの処理を呼び出す
        message = hello_logic(name, upper)

        # 出力形式の制御
        if json_output:
            output = {"message": message}
            print(json.dumps(output, ensure_ascii=False))
        else:
            print(message)

        # ★終了コード: 0（成功）
        sys.exit(0)

    except Exception as e:
        _handle_error(e, ctx)


# ============================================================
# ★サブコマンド2: sum
# ============================================================
@app.command(name="sum")
def sum_cmd(
    ctx: typer.Context,
    numbers: Annotated[
        list[int],
        typer.Argument(help="合計する整数のリスト（1つ以上必須）"),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="JSON形式で出力"),
    ] = False,
):
    """
    複数の整数を合計する

    例:
        mytool sum 1 2 3
        mytool sum 10 20 30 --json
    """
    try:
        # core.pyの処理を呼び出す
        result = sum_logic(numbers)

        # 出力形式の制御
        if json_output:
            output = {"sum": result, "count": len(numbers)}
            print(json.dumps(output, ensure_ascii=False))
        else:
            print(f"合計: {result}")

        # ★終了コード: 0（成功）
        sys.exit(0)

    except ValueError as e:
        # ★引数エラーの場合は終了コード2
        _handle_error(e, ctx, exit_code=2)
    except Exception as e:
        _handle_error(e, ctx)


# ============================================================
# ★サブコマンド3: check
# ============================================================
@app.command()
def check(
    ctx: typer.Context,
    mode: Annotated[
        str,
        typer.Option(
            "--mode",
            help="チェックモード: 'ok'なら成功、'fail'なら失敗",
        ),
    ],
):
    """
    チェック処理を実行（成功/失敗のシミュレーション）

    例:
        mytool check --mode ok
        mytool check --mode fail
        mytool check --mode fail --verbose
    """
    try:
        # core.pyの処理を呼び出す
        check_logic(mode)

        print("✓ チェック成功")
        # ★終了コード: 0（成功）
        sys.exit(0)

    except RuntimeError as e:
        # ★意図的な失敗の場合は終了コード1
        _handle_error(e, ctx, exit_code=1)
    except ValueError as e:
        # ★引数エラーの場合は終了コード2
        _handle_error(e, ctx, exit_code=2)
    except Exception as e:
        _handle_error(e, ctx)


# ============================================================
# エラーハンドリング用ヘルパー関数
# ============================================================
def _handle_error(
    error: Exception,
    ctx: typer.Context,
    exit_code: int = 1,
):
    """
    エラーを適切に処理して終了する

    Args:
        error: 発生した例外
        ctx: typerコンテキスト（共通オプションを取得するため）
        exit_code: 終了コード（デフォルト: 1）

    ★例外の握りつぶし禁止：
    - 通常時: ユーザー向けの短いエラーメッセージのみ
    - --verbose時: スタックトレースも表示
    """
    # 共通オプションの取得
    verbose = False
    if ctx.obj and isinstance(ctx.obj, dict):
        verbose = ctx.obj.get("verbose", False)

    # エラーメッセージを表示
    print(f"エラー: {error}", file=sys.stderr)

    # verboseモードの場合はスタックトレースも表示
    if verbose:
        print("\n--- スタックトレース ---", file=sys.stderr)
        traceback.print_exc()

    # ★終了コードを指定して終了
    sys.exit(exit_code)


# ============================================================
# ★メインエントリポイント
# ============================================================
def main():
    """
    メインエントリポイント

    pyproject.tomlの[project.scripts]で指定されている関数。
    これにより、`mytool` コマンドでこの関数が呼ばれる。
    """
    app()


if __name__ == "__main__":
    # 直接このファイルを実行した場合（python mytool/cli.py）
    main()

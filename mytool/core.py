"""
コアロジック - 各コマンドの実際の処理を実装

CLIの入口（cli.py）とビジネスロジック（このファイル）を分離することで、
テストしやすく、再利用しやすいコードになる。
"""


def hello_logic(name: str, upper: bool = False) -> str:
    """
    挨拶メッセージを生成する

    Args:
        name: 挨拶する相手の名前
        upper: Trueの場合は大文字にする

    Returns:
        挨拶メッセージ
    """
    message = f"Hello, {name}!"
    if upper:
        message = message.upper()
    return message


def sum_logic(numbers: list[int]) -> int:
    """
    数値のリストを合計する

    Args:
        numbers: 整数のリスト

    Returns:
        合計値

    Raises:
        ValueError: numbersが空の場合
    """
    if not numbers:
        raise ValueError("少なくとも1つの数値が必要です")
    return sum(numbers)


def check_logic(mode: str) -> bool:
    """
    チェック処理を実行する（成功/失敗をシミュレート）

    Args:
        mode: "ok" または "fail"

    Returns:
        成功した場合はTrue

    Raises:
        RuntimeError: mode="fail"の場合
        ValueError: mode が不正な場合
    """
    if mode == "ok":
        return True
    elif mode == "fail":
        raise RuntimeError("意図的な失敗: チェックモードが'fail'に設定されています")
    else:
        raise ValueError(f"不正なモード: {mode}。'ok'または'fail'を指定してください")

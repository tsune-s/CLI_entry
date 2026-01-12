"""
★ここが「入口統一」の仕組み（その1）：__main__.py

このファイルが存在することで、`python -m mytool` でパッケージを実行できる。
Pythonが `python -m mytool` を実行すると、このファイルが呼ばれる。
"""

from mytool.cli import main

if __name__ == "__main__":
    # cli.pyのmain関数を呼び出す
    # ★終了コードの制御はここではなく、cli.py内で行う
    main()

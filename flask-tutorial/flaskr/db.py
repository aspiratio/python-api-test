import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,  # データ型解析オプション
        )
        g.db.row_factory = (
            sqlite3.Row
        )  # dictのように振る舞う行を返すようにできる。つまり列名で列にアクセスできる

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("データベースを初期化しました")


def init_app(app):
    app.teardown_appcontext(
        close_db
    )  # レスポンスを返した後のクリーンアップを行っているときに引数に渡した関数を呼ぶ
    app.cli.add_command(
        init_db_command
    )  # flaskコマンドを使って呼び出すことができる新しいコマンドを追加
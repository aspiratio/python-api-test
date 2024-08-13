import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    # 正常系：アプリケーションコンテキスト内では get_db は呼び出されるたびに同じ接続を返す
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # 異常系：アプリケーションコンテキストを抜けた後はDBに接続できないことを確認
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    # 異常系：上記のエラーメッセージに closed という文字列があることを確認
    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "初期化" in result.output
    assert Recorder.called

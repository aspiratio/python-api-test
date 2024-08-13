import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    # 正常系：登録ページのGETリクエストが成功する
    assert client.get("/auth/register").status_code == 200

    # 正常系：登録のPOSTリクエストが成功する
    response = client.post("/auth/register", data={"username": "a", "password": "a"})

    # 正常系：ログインページにリダイレクトする
    assert response.headers["Location"] == "/auth/login"

    # 正常系：登録したユーザーが存在する
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )


# 異常系：バリデーションエラーのメッセージが返却される
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", "ユーザーネームは必須です"),  # ユーザーネームがない
        ("a", "", "パスワードは必須です"),  # パスワードがない
        ("test", "test", "既に登録されています"),  # ユーザーが登録済み
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.get_data(as_text=True)


def test_login(client, auth):
    # 正常系：ログインページのGETリクエストが成功する
    assert client.get("/auth/login").status_code == 200

    # 正常系：ログインのPOSTリクエストが成功する
    response = auth.login()

    # 正常系：トップページにリダイレクトする
    assert response.headers["Location"] == "/"

    # 正常系：ログインしたユーザーの情報をセッションが持っている
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


# 異常系：不正なユーザーネームやパスワードではログインできない
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", "存在しないユーザー名です"), ("test", "a", "パスワードが違います")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.get_data(
        as_text=True
    )  # as_text=True でバイト文字列をデコードする


def test_logout(client, auth):
    auth.login()

    # 正常系：セッションのユーザー情報が残っていない
    with client:
        auth.logout()
        assert "user_id" not in session

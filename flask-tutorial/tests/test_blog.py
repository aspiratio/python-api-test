import pytest
from flaskr.db import get_db


def test_index(client, auth):
    # 正常系：ログインしていないユーザーがトップページにアクセスでき、所定の文字列が表示される
    response = client.get("/")
    assert "Log In" in response.get_data(as_text=True)
    assert "Register" in response.get_data(as_text=True)

    # 正常系：ログインしているユーザーがトップページにアクセスでき、所定の文字列が表示される
    auth.login()
    response = client.get("/")
    assert "Log Out" in response.get_data(as_text=True)
    assert "test title" in response.get_data(as_text=True)
    assert "by test on 2018-01-01" in response.get_data(as_text=True)
    assert "test\nbody" in response.get_data(as_text=True)
    assert 'href="/1/update"' in response.get_data(as_text=True)


# 異常系：ログインしていないユーザーが新規作成、編集、削除のリクエストを送るとログインページに遷移する
@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
        "/1/delete",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # ポストのユーザーIDを変更する
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # 異常系：他のユーザーのポストは編集できない
    assert client.post("/1/update").status_code == 403
    # 異常系：他のユーザーのポストは削除できない
    assert client.post("/1/delete").status_code == 403
    # 異常系：他のユーザーのポストの編集ページリンクは見えない
    assert 'href="/1/update"' not in client.get("/").get_data(as_text=True)


# 異常系：ポストが存在しないと編集や削除は実行できない
@pytest.mark.parametrize(
    "path",
    (
        "/2/update",
        "/2/delete",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    # 正常系：ログインしていれば新規作成ページにアクセスできる
    assert client.get("/create").status_code == 200

    # 正常系：送信した記事がDBに登録される
    client.post("/create", data={"title": "created", "body": ""})
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2  # 既に登録済みの記事＋新規登録の記事で2件


def test_update(client, auth, app):
    auth.login()
    # 正常系：ログインしたユーザー自身のポストは更新ページにアクセスできる
    assert client.get("/1/update").status_code == 200

    # 正常系：更新情報がDBに反映されている
    client.post("/1/update", data={"title": "updated", "body": ""})
    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


# 異常系：タイトルが無いとポストの新規作成や更新ができない
@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert "タイトルは必須です" in response.get_data(as_text=True)


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    # 削除後はトップページに遷移する
    assert response.headers["Location"] == "/"

    # 削除したポストがDBに存在しない
    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None

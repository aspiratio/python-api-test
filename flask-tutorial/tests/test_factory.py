from flaskr import create_app


def test_config():
    assert (
        not create_app().testing
    )  # デフォルトの設定では testing モードが False であることを確認
    assert create_app(
        {"TESTING": True}
    ).testing  # testing モードが True になることを確認


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"  # バイト型の Hello, World が帰ってくる

import os

from flask import Flask


def create_app(test_config=None):
    # アプリの作成と設定
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # インスタンスフォルダにconfig.pyが存在する時だけロードする（見つからなくてもエラーを発生させない）
        app.config.from_pyfile("config.py", silent=True)
    else:
        # test_configが渡された時はそれをロードする
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)  # インスタンスフォルダがなければ作る
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    return app

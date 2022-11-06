from flask import Flask

# Flaskのインスタンス作成
app = Flask(__name__)

# ルーティングの指定
@app.route("/")
def index():
	return "index page" # HTMLを返す

# ルーティングの指定
@app.route("/hello")
def hello():
	return "<h1>hello, world</h1>"
# 実行時のシェルコマンド $ FLASK_APP=get_articles.py flask run

from flask import Flask

app = Flask(__name__)

# URLとメソッドの指定
@app.route("/articles", methods=["GET"])
def get_articles():
	title = "Qiita Title"
	url = "https://qiita.com"
	
	# JSON形式でレスポンス
	return {
		"title": title,
		"url": url,
	}

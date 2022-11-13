import sqlite3
from flask import Flask,render_template,request,g

app = Flask(__name__)

# DB情報を取得する関数を用意しておく（gはリクエストごとに異なる）
# もし同じリクエストの中でget_dbが2回呼び出された場合、新しいconnectionを作成する代わりに、再利用される
def get_db():
	if "db" not in g:
		# DB接続 ファイルがなければ作成する 戻り値をFlaskのグローバル変数に保存
		g.db = sqlite3.connect("TestDB.db")
	return g.db

def get_query(query_file_path):
  with open(query_file_path, 'r', encoding='utf-8') as f:
    query = f.read()
  return query

@app.route("/")
def index():
	
	# データベースを開く
	con = get_db()
	
	# テーブル「item_list」の有無を確認 execute()で中に書いたSQLを実行できる
	cur = con.execute("SELECT count(*) FROM sqlite_master WHERE TYPE='table' AND name='item_list'")
	
	for row in cur:
		if row[0] == 0:
			# テーブル「item_list」がなければ作成する
			cur.execute("CREATE TABLE item_list(code INTEGER PRIMARY KEY, item_name STRING, price INTEGER)")
			# レコードを作る
			cur.execute(
				"""INSERT INTO item_list(code, item_name, price) 
          values(1, '苺のショートケーキ', 350),
          (2, 'チョコケーキ', 380),
          (3, 'パインケーキ', 380),
          (4, 'バニラアイス', 180),
          (5, 'チョコアイス', 200),
          (6, '紅茶アイス', 180),
          (7, 'りんごのアップルパイ', 250),
          (8, 'ホットコーヒー', 100),
          (9, 'コーラ', 120),
          (10, 'オレンジジュース', 120)
				"""
			)
			con.commit()
	
	# 商品一覧を読み込み
	cur = con.execute(get_query("./sql/get_item_list.sql"))
	# fetchallでcurの中身をタプルのリストとして取得する
	data = cur.fetchall()
	con.close()
	
	# htmlを読み込む HTML内の変数dataにdataの値を渡す
	return render_template("index.html", data = data)

@app.route("/result", methods=["POST"])
def result_post():
	# テンプレートから新規登録する商品名と値段を取得
	name = request.form["name"]
	price = request.form["price"]
	
	# データベースを開く
	con = get_db()
	
	# コードは既に登録されているコードの最大値＋１の値で新規登録を行う
	cur = con.execute("SELECT MAX(code) AS max_code FROM item_list")
	for row in cur:
		new_code = row[0] + 1
	cur.close()
	
	# 登録処理
	sql = "INSERT INTO item_list(code, item_name, price)values({}, '{}', {})".format(new_code, name, price)
	con.execute(sql)
	con.commit()
	
	# 一覧再読み込み
	cur = con.execute("SELECT * FROM item_list ORDER BY code")
	data = cur.fetchall()
	con.close()
	
	return render_template("index.html", data = data)
	
if __name__ == "__main__":
	app.debug = True
	app.run(host="localhost")
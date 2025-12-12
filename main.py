from flask import (
    Flask, render_template, redirect,
    url_for, request, flash
)
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
import mysql.connector
from datetime import datetime

from models import User, TodoList, Task

app = Flask(__name__)
app.secret_key = "secret_key" # 最好是用一串無意義，結合數字、符號、字母的字串當作你正式系統編碼的種子

# ----------------- 資料庫連線配置 -----------------
DB_CONFIG = {
    'host' : 'localhost',   # 主機名稱
    'user' : 'root',        # 帳號
    'password' : '',        # 密碼
    'database' : 'flaskfinal'     # 資料庫名稱
}

# ------------ 建立並回傳 MySQL 連線物件 -----------
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"資料庫連線錯誤: {err}")
        return None

# 建立一條DB全域連線
conn = get_db_connection()

# ----------------- flask_login 設定 -----------------
login_manager = LoginManager(app)
login_manager.login_view = "login"  # 未登入時會導向 /login
login_manager.login_message = "請先登入"    # 預設 flash 訊息

@login_manager.user_loader
def load_user(user_id):
    """透過 session 裡的 user_id 從資料庫載入 User 物件"""
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(row["id"], row["username"], row["password_hash"])
    return None

# ----------------- 路由區 -----------------
@app.route("/")
@login_required
def index():
    # current_user 會是上面 User 類別的實例
    cur = conn.cursor(dictionary=True)
    
    # 1. 取得使用者的所有列表
    cur.execute("SELECT * FROM todo_list WHERE owner_id = %s", (current_user.id,))
    list_rows = cur.fetchall()
    
    my_lists = []
    for list_row in list_rows:
        # Create TodoList object
        # fix: handle created_at if it exists in row, else None
        # Assuming DB schema matches SQL file which has created_at
        current_list = TodoList(
            list_row["id"], 
            list_row["title"], 
            list_row["owner_id"], 
            list_row.get("created_at")
        )
        
        # 2. 取得該列表的所有任務 (為了計算 task|length)
        cur.execute("SELECT * FROM task WHERE list_id = %s", (current_list.id,))
        task_rows = cur.fetchall()
        
        # 將任務資料轉為 Task 物件並附加到 list 物件上
        # 這裡我們動態附加一個 tasks 屬性給 TodoList 實例，
        # 這樣 template 裡的 list.tasks|length 就能運作
        current_list.tasks = []
        for task_row in task_rows:
            task_obj = Task(
                task_row["id"],
                task_row["list_id"],
                task_row["content"],
                task_row.get("due_date"),
                task_row.get("is_completed"),
                task_row.get("created_at")
            )
            current_list.tasks.append(task_obj)
            
        my_lists.append(current_list)

    cur.close()
    
    return render_template("dashboard.html", message=current_user.username, my_lists=my_lists)

@app.route("/login", methods=["GET", "POST"])
def login():
    # POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and check_password_hash(row["password_hash"], password):
            user = User(row["id"], row["username"], row["password_hash"])
            login_user(user)  # 建立登入狀態
            flash("登入成功")
            return redirect(url_for("index"))
        else:
            flash("帳號或密碼錯誤")
            return render_template(
                "auth.html",
                mode="login",
                message="帳號或密碼錯誤。"
            )
    else: # GET, POST以外的其他方法
        return render_template("auth.html", mode="login", message="請輸入帳號和密碼。")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        cur = conn.cursor(dictionary=True)
        # 檢查帳號是否存在
        cur.execute("SELECT id FROM user WHERE username = %s", (username,))
        existing = cur.fetchone()
        if existing:
            cur.close()
            flash("帳號已存在")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO user (username, email, password_hash) "
            "VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        conn.commit()
        cur.close()

        flash("註冊成功，請登入")
        return redirect(url_for("login"))
    else: # GET, POST以外的其他方法
        return render_template(
            "auth.html",
            mode="register",
            message="請輸入帳號、信箱和密碼。"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()  # 清除登入狀態
    flash("已登出")
    return redirect(url_for("login"))


@app.route("/create_list", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method == "POST":
        title = request.form.get("title")
        owner_id = current_user.id

        cur = conn.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO todo_list (title, owner_id, created_at) VALUES (%s, %s, NOW())",
            (title, owner_id)
        )
        conn.commit()
        cur.close()

        flash("建立成功")
        return redirect(url_for("index"))
    
    return render_template("create_list.html")

@app.route('/list/<int:list_id>')
@login_required
def view_list(list_id):
    cur = conn.cursor(dictionary=True)
    
    # 1. Fetch List
    cur.execute("SELECT * FROM todo_list WHERE id = %s", (list_id,))
    list_row = cur.fetchone()
    
    if not list_row:
        cur.close()
        return render_template('err_404.html', message='List not found'), 404

    current_list = TodoList(
        list_row["id"], 
        list_row["title"], 
        list_row["owner_id"], 
        list_row.get("created_at")
    )

    # 2. Fetch Owner
    cur.execute("SELECT * FROM user WHERE id = %s", (current_list.owner_id,))
    user_row = cur.fetchone()
    if user_row:
        current_list.owner = User(user_row["id"], user_row["username"], user_row["password_hash"])
    else:
        current_list.owner = None # Should not happen ideally

    # 3. Fetch Tasks
    cur.execute("SELECT * FROM task WHERE list_id = %s", (current_list.id,))
    task_rows = cur.fetchall()
    
    current_list.tasks = []
    for task_row in task_rows:
        task_obj = Task(
            task_row["id"],
            task_row["list_id"],
            task_row["content"],
            task_row.get("due_date"),
            task_row.get("is_completed"),
            task_row.get("created_at")
        )
        current_list.tasks.append(task_obj)

    cur.close()

    return render_template('list_detail.html', todo_list=current_list, now=datetime.now(), logs=[])

@app.route('/list/<int:list_id>/delete')
@login_required
def delete_list(list_id):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM todo_list WHERE id = %s", (list_id,))
    todo_list = cur.fetchone()
    if todo_list['owner_id'] != current_user.id:
        flash('Permission denied.')
        return redirect(url_for('dashboard'))
    
    cur.execute("DELETE FROM todo_list WHERE id = %s", (list_id,))
    conn.commit()
    cur.close()
    flash('List deleted.')
    return redirect(url_for('dashboard'))

@app.route('/list/<int:list_id>/task/add', methods=['POST'])
@login_required
def add_task(list_id):
    # Stub for adding task
    flash("Function not implemented yet")
    return redirect(url_for('view_list', list_id=list_id))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    # Stub for toggle task
    # Need to find list_id to redirect
    flash("Function not implemented yet")
    return redirect(url_for('index')) # Fallback redirect

@app.route('/task/<int:task_id>/delete')
@login_required
def delete_task(task_id):
    # Stub for delete task
    flash("Function not implemented yet")
    return redirect(url_for('index')) # Fallback redirect

# -------- errorhandler --------
# - 404 錯誤處理 -
@app.errorhandler(404)
def page_not_found(error):
    return render_template('err_404.html', message='404 error'), 404

# - 500 錯誤處理 -
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('err_500.html', message='505 error'), 500


if __name__ == "__main__":
    app.run(debug=True)
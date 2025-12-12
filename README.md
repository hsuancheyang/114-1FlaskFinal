Flask-Login 是一個「只負責登入狀態管理」的套件，幫系統設計師處理登入、登出、記住登入、`current_user` 等機制，但「不負責」資料庫、表單驗證與密碼驗證[1][2]。

下面用條列方式把 Flask-Login 的常用功能與實務寫法整理起來，方便在專案中直接套用。

## 核心概念與流程

- Flask-Login 的工作：  
  - 把目前登入使用者的 ID 存進 session。  
  - 每次請求自動呼叫你實作的 `user_loader`，載入使用者物件到 `current_user`。  
  - 提供 `login_required` 裝飾器保護路由，以及 `login_user` / `logout_user` API[1][3]。
- 不會幫你：  
  - 不幫你存取資料庫、不幫你驗證密碼、不幫你產生表單，這些都要自己寫或搭配 Flask-WTF、SQLAlchemy 等[4][5]。

典型流程：使用者送出表單 → 你自己查 DB、驗證密碼 → 成功後呼叫 `login_user(user)` → 之後透過 `current_user` 取得登入者資訊[1][5]。

## 基本安裝與初始化

```bash
pip install flask-login
```

```python
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_random_secret"

login_manager = LoginManager(app)
login_manager.login_view = "login"         # 未登入時導向的 endpoint 名稱
login_manager.login_message = "請先登入"    # 預設 flash 訊息，可自訂
```

- `login_view`：當未登入的使用者訪問 `@login_required` 保護的路由時，要 redirect 到哪個 view。 [1][6]
- 也可以用 `login_manager.init_app(app)` 的方式在工廠模式裡註冊。 [1]

## User 類別與 UserMixin

Flask-Login 規定需要一個「使用者類別」，該類別需要有：`is_authenticated`、`is_active`、`is_anonymous`、`get_id()` 這幾個屬性/方法[1][3]。
官方建議繼承 `UserMixin` 來自動提供這些預設實作[1][7]。

```python
from flask_login import UserMixin
from your_db_model import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
```

- `UserMixin` 會自動提供：  
  - `is_authenticated`、`is_active`、`is_anonymous`、`get_id()`。 [3][8]
- 你只需要專心設計欄位（例如 email、password_hash）即可。 [5]

若是用手寫 SQL / `mysql.connector`，也可以像課堂範例那樣自訂一個 `User(UserMixin)` 把查出來的資料包起來。 [5]

## user_loader：從 session ID 載入使用者

Flask-Login 會把 `user.get_id()` 存進 session；下一個 request 來時，需要靠 `user_loader` 依 ID 把 user 撈回來。 [1][3]

```python
from flask_login import login_manager

@login_manager.user_loader
def load_user(user_id: str):
    # user_id 是 get_id() 回傳的字串
    return User.query.get(int(user_id))
```

- 回傳：  
  - 找到就回傳 `User` 實例。  
  - 找不到就回傳 `None`。 [1][8]
- 這個函式是登入後「每一次 request」都會被用來重建 `current_user`。 [1]

## login_user / logout_user 的用法

### 登入：login_user

在你自己驗證帳號密碼成功後要呼叫： [1][5]

```python
from flask import request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("帳號或密碼錯誤")
            return redirect(url_for("login"))

        login_user(user, remember=True)  # remember=True 啟用「記住我」cookie [web:61][web:65]
        flash("登入成功")
        return redirect(url_for("index"))

    return render_template("login.html")
```

常用參數： [1][9]
- `remember=True/False`：是否在 session 過期後仍記住使用者（發 remember cookie）。  
- `duration`：記住多久（`datetime.timedelta`）。  
- `fresh`：是否視為「新鮮登入」，做高風險操作可要求 fresh login。  

### 登出：logout_user

```python
from flask_login import logout_user

@app.route("/logout")
@login_required
def logout():
    logout_user()      # 清掉登入狀態與相關 cookie
    flash("已登出")
    return redirect(url_for("login"))
```

登出會把 session 中的 user ID 清掉，也會處理 remember cookie。 [1][10]

## login_required 與 current_user

### login_required

`login_required` 用來保護需要登入才能看的頁面： [1][3]  

```python
from flask_login import login_required, current_user

@app.route("/profile")
@login_required
def profile():
    return f"Hello, {current_user.email}"
```

- 未登入訪問 `/profile` 時，會自動 redirect 到 `login_view`，並帶上 `next` 參數，例如 `/login?next=/profile`。 [1][3]
- 你可以登入成功後手動 redirect 回 `next`：  

```python
from flask import request

next_url = request.args.get("next")
return redirect(next_url or url_for("index"))
```

### current_user

`current_user` 是一個 proxy 物件，指向「目前登入的使用者」，或「匿名使用者」： [1][8]  

- 登入狀態：  
  - `current_user.is_authenticated == True`。  
  - 可以直接存取你 User 類別上的屬性，例如 `current_user.id`、`current_user.email`。 [8]
- 未登入：  
  - `current_user` 會是一個 `AnonymousUserMixin` 物件。  
  - `current_user.is_authenticated == False`，沒有 `username` 等自訂屬性。 [8][11]

避免錯誤的典型寫法：  
```python
if current_user.is_authenticated:
    name = current_user.username
else:
    name = "訪客"
```

## 記住我（remember me）與 session 期限

- `login_user(user, remember=True)` 會額外設定一個「remember cookie」，即使瀏覽器關掉再開，Flask-Login 也能從 cookie 重建登入狀態。 [1][9]
- 可以用 `REMEMBER_COOKIE_DURATION` 設定持續時間：  

```python
from datetime import timedelta

app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
```

- 這與 Flask 自己的 `session.permanent` 並不相同，是獨立機制，可以同時使用。 [9][10]

## 常見錯誤與實務建議

常見坑： [8][12]
- `AnonymousUserMixin` 沒有 `username` → 在模板或 view 直接寫 `current_user.username`，但未登入。  
  - 解法：在使用前先檢查 `current_user.is_authenticated`，或直接用 `@login_required`。  
- `@login_required` 沒有生效 → endpoint 名稱拼錯、藍圖路徑不一致、`login_manager.init_app(app)` 沒有被呼叫。 [1][13]
- 重導向跳 `next` 的安全性 → 不要直接信任 `next`，應檢查是否同網域，以防 open redirect。 [1]

實務最佳做法：  
- 搭配 ORM（例如 SQLAlchemy）或現在用的 MySQL 方案，自己實作好 User model[5][7]。
- 密碼一定要用 `werkzeug.security.generate_password_hash` / `check_password_hash`。 [5]
- `SECRET_KEY` 與資料庫密碼放在環境變數，千萬不要直接寫在程式裡面[14][15]。

***

來源

[1] Flask-Login 0.7.0 documentation https://flask-login.readthedocs.io

[2] Flask-Login https://pypi.org/project/Flask-Login/

[3] Flask-Login 0.1 documentation https://docs.jinkan.org/docs/flask-login/

[4] flask-login: can't understand how it works https://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works

[5] Add Authentication to Flask Apps with Flask-Login https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

[6] 第25 天：Flask：登入系統Flask-Login - iT 邦幫忙 https://ithelp.ithome.com.tw/m/articles/10224408

[7] maxcountryman/flask-login: Flask user session management. https://github.com/maxcountryman/flask-login

[8] How to Track Current User in Flask-Login: Fixing ... https://www.pythontutorials.net/blog/how-do-you-track-the-current-user-in-flask-login/

[9] Does Flask-Login's `remember_me` override Flask's `permanent`? https://stackoverflow.com/questions/53652609/does-flask-logins-remember-me-override-flasks-permanent

[10] Flask-Login still logged in after use logouts when using remember_me https://stackoverflow.com/questions/25144092/flask-login-still-logged-in-after-use-logouts-when-using-remember-me

[11] Spurious and random "'flask_login.AnonymousUserMixin object' has no attribute" exceptions · Issue #261 · maxcountryman/flask-login https://github.com/maxcountryman/flask-login/issues/261

[12] Flask login - @login_required not working https://www.reddit.com/r/flask/comments/9y6s7r/flask_login_login_required_not_working/

[13] Beginner Question regarding Flask-Login's login_required decorator https://www.reddit.com/r/flask/comments/1j9r1qt/beginner_question_regarding_flasklogins_login/

[14] 浅谈Flask cookie与密钥的安全性 https://www.anquanke.com/post/id/170466

[15] MySQL 使用指令操作資料庫 - Clarence 的科技學習實戰筆記 https://blog.clarence.tw/2021/03/15/mysql-use-command-to-use-database/

[16] Welcome to Flask — Flask Documentation (3.1.x) https://flask.palletsprojects.com

[17] Flask-Login https://www.reddit.com/r/flask/comments/rjm63x/flasklogin/

[18] Flask-Login: Remember Me and Fresh Logins https://www.youtube.com/watch?v=CRvV9nFKoPI

[19] how to implement remember me option · Issue #319 · maxcountryman/flask-login https://github.com/maxcountryman/flask-login/issues/319

[20] Flask實作_ext_11_Flask-Login_登入狀態管理 https://hackmd.io/@shaoeChen/ryvr_ly8f

[21] How to save - "remember me" cookie in flask-login? https://www.reddit.com/r/flask/comments/199jhtu/how_to_save_remember_me_cookie_in_flasklogin/

[22] Flask Login Tutorial https://pythonbasics.org/flask-login/
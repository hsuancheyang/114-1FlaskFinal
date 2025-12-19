## 基本安裝
```bash
$ pip install Werkzeug
```

## 引用
```Python
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
```


`werkzeug.security` 最常用在「帳號密碼Hash與驗證」，典型搭配 Flask-Login 做登入系統。常用函式只有幾個：`generate_password_hash`、`check_password_hash`，其他像 `safe_str_cmp` 已經移除不要再用。[1][2]  

## 常用函式簡介

- `generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)`  
  產生「含演算法＋salt＋hash」的字串，格式類似：`pbkdf2:sha256:260000$隨機salt$雜湊值`。[3][1]
- `check_password_hash(pwhash, password)`  
  把使用者輸入的明碼，用 `pwhash` 字串裡紀錄的 method 與 salt 再算一次，比對是否相同，回傳 True/False。[3][4]

## 基本使用範例

### 註冊：把明碼轉成雜湊存進資料庫

```python
from werkzeug.security import generate_password_hash

plain_password = "user_input_password"

# 建議保留預設 method（pbkdf2:sha256），只調整 salt_length 即可
password_hash = generate_password_hash(plain_password)  # 回傳字串
# 把 password_hash 存到資料庫的 password_hash 欄位
```
  

說明：  
- 同一個密碼每次呼叫 `generate_password_hash` 都會得到不同結果，因為每次 salt 都是隨機，這是正常現象。[5]
- 驗證時不用自己存 salt，因為它已經包含在 `password_hash` 字串裡了。[15][5]

### 登入：從資料庫撈出雜湊，比對輸入的密碼

```python
from werkzeug.security import check_password_hash

# 假設從 DB 撈到的欄位
row = {
    "username": "alice",
    "password_hash": password_hash_from_db,
}

input_password = "user_login_input"

if check_password_hash(row["password_hash"], input_password):
    # 密碼正確 → 執行 login_user(user) 等
    ...
else:
    # 密碼錯誤
    ...
```
  

## 參數設定與常見選項

- `method`  
  - 預設：`"pbkdf2:sha256"`，安全性足夠且官方建議。[6]
  - 可以寫成 `"pbkdf2:sha256:260000"` 指定 iteration 次數（越大越慢但越安全）。[6]
  - 不要用 `md5`、`sha1` 這種簡單雜湊當最終方案，僅適合「相容舊系統」。[3][6]
- `salt_length`  
  - 預設 16，平常不需要改；變長只是增加隨機度，資料庫欄位記得給足夠長度（例如 VARCHAR(255)）。[5][6]

範例：  

```python
# 指定使用 pbkdf2:sha256 並把迭代次數調高
password_hash = generate_password_hash(
    plain_password,
    method="pbkdf2:sha256:260000",
    salt_length=16,
)
```
  

## 舊版 safe_str_cmp 的狀況

- `from werkzeug.security import safe_str_cmp` 在新版 Werkzeug 已經拿掉，會 ImportError。[2][7]
- 如果遇到第三方套件還在 import `safe_str_cmp`（常見舊版 Flask-Bcrypt / Flask-Login），解法通常是：  
  - 升級該套件（例如 `pip install --upgrade flask-bcrypt`），新版會改用 `hmac.compare_digest`。[27]
  - 或是把 Werkzeug 版本鎖在 2.0.x（暫時性方案，不建議長期使用）。[7][8]

## 結合 Flask-Login / MySQL 的典型流程提示

與你現有的 Flask + `mysql.connector` 專案結合時，大致流程是：  

1. 註冊時：
   - 從表單取得明碼，呼叫 `generate_password_hash`。
   - 將結果存入 `users.password_hash` 欄位。  
2. 登入時：
   - 依 username 從 DB 撈出那筆 user。
   - 用 `check_password_hash(row["password_hash"], form_password)` 驗證。
   - 成功就呼叫 `login_user(user)`。  

這部分和整合 Flask-Login 的範例是完全相容的，只要把密碼欄位設成雜湊即可。[5][4]

***

如果需要，可以直接貼出你的 Flask 登入／註冊程式碼，幫你把 `generate_password_hash` / `check_password_hash` 寫進去並標註每一行的用途。

來源
[1] Werkzeug安全模块深度解析：密码哈希和文件安全处理的终极指南 https://blog.csdn.net/gitblog_01196/article/details/151419128

[2] Python：Werkzeug.security对密码进行加密和校验原创 https://blog.csdn.net/mouday/article/details/115858774

[3] How can I utilize werkzeug.security's check_password_hash function to verify correct password against existing salted sha1 password hashes https://stackoverflow.com/questions/58452887/how-can-i-utilize-werkzeug-securitys-check-password-hash-function-to-verify-cor

[4] generate_password_hash & check_password_hash https://tanxy.club/2022/encryption-algorithms-in-flask

[5] werkzeug:generate_password_hash()函数关于同一密码 ... https://blog.csdn.net/Miao_Hen/article/details/105157765

[6] werkzeug.security.generate_password_hash() について調べた https://pancokeiba.hatenablog.com/entry/2023/10/12/052204

[7] cannot import name 'safe_str_cmp' from 'werkzeug.security' https://stackoverflow.com/questions/71652965/importerror-cannot-import-name-safe-str-cmp-from-werkzeug-security

[8] cannot import name: safe_str_cmp after latest release #2359 https://github.com/pallets/werkzeug/issues/2359

[9] Flask加盐密码生成和验证函数 https://flask123.sinaapp.com/article/40/

[10] Hashing Passwords in Flask with Werkzeug Utils https://testdriven.io/tips/9901c635-2ab2-42cf-a5f0-b4f3ef0b48c3/

[11] recreating pythons werkzeug.security generate_password_hash in C# https://stackoverflow.com/questions/71432845/recreating-pythons-werkzeug-security-generate-password-hash-in-c-sharp

[12] import werkzeug VS from werkzeug import security - Stack Overflow https://stackoverflow.com/questions/47688957/import-werkzeug-vs-from-werkzeug-import-security

[13] Warnings in dev environment (windows) - Development https://community.octoprint.org/t/warnings-in-dev-environment-windows/49853

[14] werkzeug.security.check_password_hash is failed · Issue #1615 · pallets/werkzeug https://github.com/pallets/werkzeug/issues/1615

[15] GitHub - jb2170/WerkzeugSecurityCLI: Generate and check werkzeug.security password hashes on the command line https://github.com/jb2170/WerkzeugSecurityCLI

[16] werkzeug.generate_password_hash — Flask API https://tedboy.github.io/flask/generated/werkzeug.generate_password_hash.html

[17] Utilities — Werkzeug Documentation (3.1.x) https://werkzeug.palletsprojects.com/en/stable/utils/

[18] What is Werkzeug? - TestDriven.io https://testdriven.io/blog/what-is-werkzeug/

[19] Cannot import name 'TextField' from 'wtforms' - App Generator https://app-generator.dev/docs/how-to-fix/import-error-safe_str_cmp-from-werkzeug.security.html

[20] werkzeug.securityでハッシュ化 - Qiita https://qiita.com/plumfield56/items/ebe5f6f5b1c884b07c99
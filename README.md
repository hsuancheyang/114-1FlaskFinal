# 114-1 Final Project: 待辦事項管理系統

## 專案描述

這是一個基於 Flask 的網頁應用程式，用於管理個人待辦事項列表。使用者可以註冊帳號、登入系統、創建待辦列表（todo-list）、添加任務(task)、標記完成狀態。系統還記錄使用者的操作日誌(activity-log)。

此專案為致理科技大學資訊管理系 114-1 學期 進修部「伺服器端網頁程式設計」課程的課堂及期末專案。

## 功能特色

- **用戶認證**：支援用戶註冊、登入和登出，使用 Flask-Login 管理。
- **待辦事項列表管理**：創建、編輯和刪除個人待辦列表。（尚缺：`修改功能`）
- **任務管理**：在列表中添加、編輯、刪除和標記完成任務。（均未完成，`期末測驗檢視重點`）
- **活動日誌**：記錄使用者的操作行為，如創建列表、添加任務等。
- **響應式設計**：使用 HTML 模板和 CSS 樣式，提供良好的用戶界面。

## 技術棧

- **後端**：Flask (Python 網頁框架)
- **前端**：HTML, CSS, Jinja2 模板
- **資料庫**：MySQL（XAMPP）
- **認證**：Flask-Login [Flask-Login.md](Flask-Login.md), Werkzeug (密碼雜湊) [werkzeug.security.md](werkzeug.security.md)
- **其他**：MySQL Connector for Python

## 安裝與設置

### 環境需求

- Python 3.13 或以上
- MySQL 伺服器

### 安裝步驟

1. **Clone或下載專案**：
   ```bash
   git clone https://github.com/hsuancheyang/114-1FlaskFinal.git
   cd 114-1FlaskFinal
   ```

2. **安裝依賴**：
   使用專案中的 `requirements.txt` 檔：
   ```bash
   pip install -r requirements.txt
   ```
   或 使用專案中的 `pyproject.toml` 檔案：
   ```bash
   pip install .
   ```

3. **設置資料庫**：
   - 安裝並啟動 MySQL 伺服器（XAMPP）。
   - 創建資料庫並執行 SQL 腳本：
     ```bash
     mysql -u root -p < sql/1. user.sql
     mysql -u root -p < sql/2. todo_list.sql
     mysql -u root -p < sql/3. task.sql
     mysql -u root -p < sql/4. activity_log.sql
     mysql -u root -p < sql/5. shared_lists.sql
     ```
   - 更新 `main.py` 中的 `DB_CONFIG` 以匹配您的 MySQL 配置。

4. **運行應用程式**：
   ```bash
   flask --app main run --debug
   ```
   應用程式將在 `http://localhost:5000` 上運行。

## 使用說明

1. **註冊帳號(route:/register, method:register(), template:auth.html)**：訪問 `/register` 頁面創建新帳號。
2. **登入(route:/login, method:login(), template:auth.html)**：使用註冊的用戶名和密碼登入。
3. **儀表板(route:/, method:index(), template:dashboard.html)**：登入後查看您的待辦列表。
4. **創建列表(route:/create_list, method:create_list(), template:create_list.html)**：在儀表板中創建新的待辦列表。
5. **檢視列表(route:/list/<int:list_id>, method:view_list(list_id), template:list_detail.html)**：檢視代辦事項內容，以及所屬任務清單。
6. **刪除列表(route:/list/delete/<int:list_id>, method:delete_list(list_id), template:dashboard.html)**:刪除代辦事項（要先確認所屬任務是否已清空才可刪除代辦事項）。
7. **添加任務(route:/list/<int:list_id>/task/add, method:add_task(list_id), template:list_detail.html)**：在列表詳情頁面添加任務，設定到期日期。（未完成）
8. **刪除任務(route:/task/<int:task_id>/delete, method:delete_task(task_id), template:list_detail.html)**：刪除任務。（未完成）
9. **修改任務()**：編輯任務內容，延展到期時間。(未完成)
10. **查看日誌(route:/logs, method:activity_log(), template:logs.html)**：檢查您的活動日誌。

## 專案結構

- `main.py`：Flask 應用程式主文件，包含路由和邏輯。
- `models.py`：資料模型定義（User, TodoList, Task）。
- `templates/`：HTML 模板文件。
- `static/`：靜態文件（如 CSS）。
- `sql/`：資料庫建表腳本。
- `pyproject.toml`：專案配置和依賴。
- `requirements.txt`：專案配置和依賴。

## 貢獻

此專案由 楊宣哲 開發。如有問題或建議，請聯繫 hc_yang@mail.chihlee.edu.tw。

## 授權

此專案僅供學習用途。

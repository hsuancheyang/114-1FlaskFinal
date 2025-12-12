from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = str(id)           # get_id() 会回傳這個
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TodoList:
    def __init__(self, id, title, owner_id, created_at=None):
        self.id = id
        self.title = title
        self.owner_id = owner_id
        self.created_at = created_at

    def __repr__(self):
        return f"<TodoList(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"

class Task:
    def __init__(self, id, list_id, content, due_date=None, is_completed=None, created_at=None):
        self.id = id
        self.list_id = list_id
        self.content = content
        self.due_date = due_date
        self.is_completed = is_completed
        self.created_at = created_at

    def __repr__(self):
        return f"<Task(id={self.id}, content='{self.content}', is_completed={self.is_completed})>"

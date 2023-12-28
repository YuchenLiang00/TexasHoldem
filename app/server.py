from flask import Flask, render_template
from flask_login import LoginManager
import webbrowser
from app.auth import auth_blueprint

app = Flask(__name__)
app.secret_key = 'xinsulion'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # 设置登录视图的端点
app.register_blueprint(auth_blueprint, url_prefix='/auth')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

@app.route('/')
def welcome_page():
    return render_template('welcome.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    return render_template('home.html')


@login_manager.user_loader
def load_user(user_id):
    # 模拟用户数据库

    return None
if __name__ == '__main__':
    # 使用线程来避免阻塞 Flask 服务器
    app.run(debug=True)

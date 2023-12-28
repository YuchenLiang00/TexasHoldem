from flask import  jsonify, render_template, request, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint

from src.gamer.player import Player

auth_blueprint = Blueprint('auth', __name__)

users = {  # TODO: user database
    'user1': {'password': 'password1'},
    'user2': {'password': 'password2'},
    # 添加更多用户 ...
}

def check_user(username, password) -> bool:
    """ 检查用户的用户名和密码是否输入正确 """
    if username in users and users[username]['password'] == password:
        return True
    else:
        return False

@auth_blueprint.route('/login', methods=["POST", "GET"])
def login():
    """ 登录逻辑 """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 简单的用户认证
        
        if check_user(username, password):
            user = Player(username)
            login_user(user)
            return jsonify({'success': True})
        else:
            # 用户名或密码输入错误
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')


@auth_blueprint.route('/')
@login_required  # 保护路由，只有登录的用户可以访问
def home():
    return render_template('home.html')


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    pass

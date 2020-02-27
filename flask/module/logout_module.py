from flask import Flask, render_template, redirect, request, jsonify, make_response, Response, session, Blueprint, current_app as app
from flask_mail import Mail, Message
from database.db_manager import DatabaseManger
from database.db_game_manager import GameDataBaseManager
from security.encryption_module import AESCipher
from database.signup_cache_manager import RedisSignUpManager
from database.login_cache_manager import RedisLoginManager
from database.search_password_cache_manager import RedisSearchPasswordManager

redis_sign_up_mng = RedisSignUpManager()
redis_login_up_mng = RedisLoginManager()
redis_search_password_mng = RedisSearchPasswordManager()
db_game_mng = GameDataBaseManager()
crypt = AESCipher()
db_manage = DatabaseManger()

blueprints = Blueprint('logout_api', __name__)

# 에러 처리
@blueprints.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404

# 로그아웃 캐시
@blueprints.route("/delet", methods=['POST', 'GET'])
def client_cache_delete():
    print("delete : " + request.form.get('email'))
    if request.method == 'POST':
        redis_login_up_mng.delete_session_token(request.form.get('email'))
        return jsonify({
            "success": "true"
        })

# 로그아웃
@blueprints.route("/logout")
def logout():
    res = make_response(redirect("/"))
    redis_login_up_mng.delete_session_token(session['email'])
    res.set_cookie("token", '', expires=0)
    session.pop('email', None)
    return res


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

blueprints = Blueprint('page', __name__)

# 메인 페이지
@blueprints.route("/main")
def main():
    #토큰이 존재하고 유효시간이 남은 경우
    if "token" in request.cookies and redis_login_up_mng.token_check(request, session['email']):
        # 만료 시간 다시 설정
        redis_login_up_mng.reset_expire(request, session['email'])
        if db_manage.manager_check(session['email']):
            return redirect("/manage")
        return render_template("main.html")
    else:
        return redirect("/")

# 관리자 페이지
@blueprints.route("/manage")
def manage():
    # manager토큰이 있고 유효시간이 만료 안됬을 때
    if redis_login_up_mng.token_check(request, session['email']) and db_manage.manager_check(session['email']):
        rows = db_manage.user_data()
        return render_template("manage.html", rows=rows)
    return redirect("/")

# 유저 정보 변경 페이지
@blueprints.route("/userinfo", methods=['POST', 'GET'])
def user_info():
    if redis_login_up_mng.token_check(request, session['email']) and db_manage.manager_check(session['email']):
        return render_template("userinfo.html", info=request.args)
        # print(request.form.get('name'))
    return redirect("/")
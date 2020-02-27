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

blueprints = Blueprint('manager', __name__)

# 유저 정보 변경
@blueprints.route("/changeinfo", methods=['POST', 'GET'])
def change_info():
    if redis_login_up_mng.token_check(request, session['email']) and db_manage.manager_check(session['email']):
        name = request.form.get('name')
        email = request.form.get('email')
        classes = request.form.get('classes')
        print(request.form)
        db_manage.user_info_revise(email, name, classes)
        return redirect("/manage")
    return redirect("/")

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

blueprints = Blueprint('password', __name__)


# 비밀번호 찾기 버튼 클릭
@blueprints.route("/inputemail")
def input_email():
    return render_template("searchemail.html")

# # 이메일 찾은 후에 이메일 전송 -> 인증 후 임시 비밀번호 발급
# @app.route("/searchemail", methods=['POST', 'GET'])
# def search_email():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         if db_manage.email_exists_check(email):     #이메일 존재시
#             key = redis_search_password_mng.create_certification_key(email)     # redis에 세션 넣기
#             email_send(key, email, 1)
#             return render_template("requestemailcertification.html")
#             #인증토큰 만들고 email로 전송 -> redis 저장 -> 클릭시 토큰 비교 -> 비밀번호 변경 창 띄우기 -> 변경
#         else:
#             error_page(error=None)


# 임시 비밀번호 발급 -> 구현 안함
@blueprints.route("/samplepassword", methods=['POST', 'GET'])
def sample_password():
    email = request.args.get('email')
    uuid = request.args.get('uuid')

    # redis의 값과 확인하고 같으면 redis 데이터 지우기
    if redis_search_password_mng.click_url_certification(email, uuid):
        sample_pw = redis_search_password_mng.create_sample_pw()

        db_manage.revise_password(email, sample_pw)
        return render_template('samplepassword.html', password=sample_pw)
    else:
        return error_page(error=None)


# 패스워드 변경 페이지
@blueprints.route("/revisepasswordpage")
def revise_password_page():
    return render_template("revisepassword.html")

# 패스워드 변경
@blueprints.route("/revisepassword", methods=['POST', 'GET'])
def revise_password():
    if request.method == 'POST':
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')
        if pw1 != pw2 or request.cookies.get('token') != redis_login_up_mng.get_user_uuid(session['email']):
            return jsonify({
                "flag": "false"
            })
        db_manage.revise_password(session['email'], pw1)
        return jsonify({
            "flag": "true"
        })
    return jsonify({
        "flag": "false"
    })

# 에러 처리
@blueprints.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404
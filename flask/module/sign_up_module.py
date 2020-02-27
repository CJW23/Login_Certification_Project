from flask import Flask, render_template, redirect, request, jsonify, make_response, Response, session, Blueprint, current_app
from flask_mail import Mail, Message
from database.db_manager import DatabaseManger
from database.db_game_manager import GameDataBaseManager
from security.encryption_module import AESCipher
from database.signup_cache_manager import RedisSignUpManager
from database.login_cache_manager import RedisLoginManager
from database.search_password_cache_manager import RedisSearchPasswordManager

URL = "http://192.168.0.116:8082"

redis_sign_up_mng = RedisSignUpManager()
redis_login_up_mng = RedisLoginManager()
redis_search_password_mng = RedisSearchPasswordManager()
db_game_mng = GameDataBaseManager()
crypt = AESCipher()
db_manage = DatabaseManger()

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cjw7242@gmail.com'
app.config['MAIL_PASSWORD'] = 'yqtmojlkkcxrwnbv'
mail = Mail(app)

blueprints = Blueprint('sign_up', __name__)

# 회원가입
@blueprints.route("/signup")
def signup():
    return render_template("signup.html")

# 이메일 인증 메일 전송 API
@blueprints.route("/email", methods=['POST', 'GET'])
def email_certification():
    email_address = request.args.get('address')
    if db_manage.email_overlap_check(email_address):
        # redis에 이메일 인증키 저장
        email_uuid = redis_sign_up_mng.create_certification_key(email_address)
        email_send(email_uuid, email_address, 0)
        return jsonify({
            "check": "true"
        })
    return jsonify({
        "check": "false"
    })

# 이메일 인증 확인 체크
@blueprints.route("/emailcheck", methods=['POST', 'GET'])
def email_check():
    email_address = request.args.get('address')
    if redis_sign_up_mng.check_certification_key(email_address):
        return jsonify({
            "complete": "true"
        })
    return jsonify({
            "complete": "false"
    })

# 이메일 인증 url 클릭
@blueprints.route("/certification", methods=['POST', 'GET'])
def click_certification_url():
    email_address = request.args.get('email')
    uuid = request.args.get('uuid')
    print("??? : " + str(email_address))
    print("??? : " + str(uuid))
    if redis_sign_up_mng.click_url_certification(email_address, uuid):
        return render_template("complete_certification.html")
    else:
        return error_page(error=None)

# 회원가입 버튼
@blueprints.route("/clicksignup", methods=['POST', 'GET'])
def click_sign_up():
    if request.method == 'POST':
        db_manage.insert_certification(request.form)
    return redirect("/")


# 인증 이메일 전송
# flag = 0 : 회원가입 이메일
# flag = 1 : 비밀번호 찾기 이메일
def email_send(uuid, user_email, flag):
    if flag == 0:
        with app.app_context():
            url = URL + "/certification?email=%s&uuid=%s" % (user_email, uuid)
            msg = Message(
                subject="회원가입 인증",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[user_email],  # use your email for testing
                body=url)
            mail.send(msg)
    else:
        with app.app_context():
            url = URL + "/samplepassword?email=%s&uuid=%s" % (user_email, uuid)
            msg = Message(
                subject="임시 비밀번호",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[user_email],  # use your email for testing
                body=url)
            mail.send(msg)

# 에러 처리
@blueprints.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404


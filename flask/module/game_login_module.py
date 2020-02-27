from flask import Flask, render_template, redirect, request, jsonify, make_response, Response, session, Blueprint
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

blueprints = Blueprint('game_login', __name__)

# 로그인페이지
@blueprints.route("/")
def login():
    if session.get('email') is not None:
        if redis_login_up_mng.token_check(request, session['email']):
            redis_login_up_mng.reset_expire(request, session['email'])
            redis_login_up_mng.reset_expire(request, session['email'])        #시간 초기
            return redirect("/main")
    return render_template("index.html")

# 게임 클라이언트 로그인
@blueprints.route("/clientlogin", methods=['POST', 'GET'])
def client_login():
    if request.method == 'POST':
        print(request.form.get('email'))
        if db_manage.login_check(request.form.get('email'), request.form.get('password')):
            email = request.form.get('email')
            if redis_login_up_mng.token_exists(email):      #이미 접속한 아이디라면
                print("overlap")
                return jsonify({
                    "email": "",
                    "token": "",
                    "id": "",
                    "login": "overlap"
                })
            print("여길 왜 들어와")
            token = redis_login_up_mng.insert_uuid_cookie(email)  # redis에 토큰 저장
            info = db_manage.user_info(email)
            return jsonify({
                "email": email,
                "token": token,
                "id": info['id'],
                "username": info['username'],
                "login": "true"
            })
        return jsonify({
            "email": "",
            "token": "",
            "id": "",
            "login": "false"
        })

# Ajax에서의 로그인 처리
@blueprints.route("/checklogin", methods=['GET', 'POST'])
def check_login():
    if request.method == 'POST':
        if db_manage.login_check(request.form.get('email'), request.form.get('password')):
            return jsonify({
                "check": "true"
            })
        return jsonify({
            "check": "false"
        })

# 로그인 시도
@blueprints.route("/trylogin", methods=['POST', 'GET'])
def try_login():
    #일치할 시 redis에 email, value(uuid) expire적용후 저장 -> 쿠키에 저장
    if request.method == 'POST':
        if db_manage.login_check(request.form.get('email'), request.form.get('password')):
            email = request.form.get('email')
            session['email'] = email
            print('세션 : '+str(session['email']))
            token = redis_login_up_mng.insert_uuid_cookie(email)       #redis에 토큰 저장
            res = make_response(redirect("/main"))
            res.set_cookie("token", str(token))                     #쿠키 설정
            return res
    return error_page(error=None)

# 게임 레디스 캐시 체크
@blueprints.route("/clientusercache", methods=['POST', 'GET'])
def client_cache_check():
    if request.method == 'POST':
        return redis_login_up_mng.get_user_uuid(request.form.get('email'))


# 관리자 체크
@blueprints.route("/checkmanager", methods=['POST', 'GET'])
def check_manager():
    if request.method == 'POST':
        email = request.form.get('email')
        if db_manage.manager_check(email):     #관리자면
            return jsonify({
                "manager": "true"
            })
        return jsonify({
            "manager": "false"
        })

# 에러 처리
@blueprints.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404
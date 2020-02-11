from flask import Flask, render_template, redirect, request, jsonify, make_response, Response, session
from flask_mail import Mail, Message
from database.dbManger import DatabaseManger
from security.encryptionModule import AESCipher
from database.SignUpCacheManager import RedisSignUpManager
from database.LoginCacheManager import RedisLoginManager
from database.SearchPasswordCacheManager import RedisSearchPasswordManager

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cjw7242@gmail.com'
app.config['MAIL_PASSWORD'] = 'yqtmojlkkcxrwnbv'
app.secret_key = b'1234wqerasdfzxcv'


mail = Mail(app)
redis_sign_up_mng = RedisSignUpManager()
redis_login_up_mng = RedisLoginManager()
redis_search_password_mng = RedisSearchPasswordManager()
crypt = AESCipher()
dbMng = DatabaseManger()


# test페이지
@app.route("/test")
def test():
    return jsonify({
        "nicName": "success",
        "token": "success2"
    })
# 페이지 캐시 관
@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

#로그인페이지
@app.route("/")
def login():
    if session.get('email') is not None:
        if redis_login_up_mng.token_check(request, session['email']):
            redis_login_up_mng.reset_expire(request, session['email'])
            print("쿠키 있음aaa")
            redis_login_up_mng.reset_expire(request, session['email'])        #시간 초기
            return redirect("/main")
    return render_template("index.html")

#비밀번호 찾기 버튼 클릭
@app.route("/inputemail")
def input_email():
    return render_template("searchemail.html")

#회원가입
@app.route("/signup")
def signup():
    return render_template("signup.html")

#이메일 인증 메일 전송 API
@app.route("/email", methods=['POST', 'GET'])
def email_certification():
    email_address = request.args.get('address')
    if dbMng.email_overlap_check(email_address):
        # redis에 이메일 인증키 저장
        email_uuid = redis_sign_up_mng.create_certification_key(email_address)
        email_send(email_uuid, email_address, 0)
        return jsonify({
            "check": "true"
        })
    return jsonify({
        "check": "false"
    })

#이메일 인증 확인 체크
@app.route("/emailcheck", methods=['POST', 'GET'])
def email_check():
    email_address = request.args.get('address')
    if redis_sign_up_mng.check_certification_key(email_address):
        return jsonify({
            "complete": "true"
        })
    return jsonify({
            "complete": "false"
    })

#이메일 인증 url 클릭
@app.route("/certification", methods=['POST', 'GET'])
def click_certification_url():
    email_address = request.args.get('email')
    uuid = request.args.get('uuid')
    print("??? : " + str(email_address))
    print("??? : " + str(uuid))
    if redis_sign_up_mng.click_url_certification(email_address, uuid):
        return render_template("complete_certification.html")
    else:
        return error_page(error=None)

#회원가입 버튼
@app.route("/clicksignup", methods=['POST', 'GET'])
def click_sign_up():
    if request.method == 'POST':
        dbMng.insert_certification(request.form)
    return redirect("/")

#에러 처리
@app.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404

# ajax에서의 로그인 처리
@app.route("/checklogin", methods=['GET', 'POST'])
def check_login():
    if request.method == 'POST':
        if dbMng.login_check(request.form.get('email'), request.form.get('password')):
            return jsonify({
                "check": "true"
            })
        return jsonify({
            "check": "false"
        })

#로그인 시도
@app.route("/trylogin", methods=['POST', 'GET'])
def try_login():
    #일치할 시 redis에 email, value(uuid) expire적용후 저장 -> 쿠키에 저장
    if request.method == 'POST':
        if dbMng.login_check(request.form.get('email'), request.form.get('password')):
            email = request.form.get('email')
            session['email'] = email
            print('세션 : '+str(session['email']))
            token = redis_login_up_mng.insert_uuid_cookie(email)       #redis에 토큰 저장
            res = make_response(redirect("/main"))
            res.set_cookie("token", str(token))                     #쿠키 설정
            return res
    return error_page(error=None)

#게임 클라이언트 로그인
@app.route("/clientlogin", methods=['POST', 'GET'])
def client_login():
    if request.method == 'POST':
        print(request.form.get('email'))
        if dbMng.login_check(request.form.get('email'), request.form.get('password')):
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
            id = dbMng.user_id(email)
            return jsonify({
                "email": email,
                "token": token,
                "id": id,
                "login": "true"
            })
        return jsonify({
            "email": "",
            "token": "",
            "id": "",
            "login": "false"
        })

#게임 레디스 캐시 체크
@app.route("/clientusercache", methods=['POST', 'GET'])
def client_cache_check():
    if request.method == 'POST':
        return redis_login_up_mng.get_user_uuid(request.form.get('email'))


@app.route("/delet", methods=['POST', 'GET'])
def client_cache_delete():
    print("delete : " + request.form.get('email'))
    if request.method == 'POST':
        redis_login_up_mng.delete_session_token(request.form.get('email'))
        return jsonify({
            "success" : "true"
        })

#메인 페이지
@app.route("/main")
def main():
    #토큰이 존재하고 유효시간이 남은 경우
    if "token" in request.cookies and redis_login_up_mng.token_check(request, session['email']):
        # 만료 시간 다시 설정
        redis_login_up_mng.reset_expire(request, session['email'])
        if dbMng.manager_check(session['email']):
            return redirect("/manage")
        return render_template("main.html")
    else:
        return redirect("/")

#관리자 페이지
@app.route("/manage")
def manage():
    #manager토큰이 있고 유효시간이 만료 안됬을 때
    if redis_login_up_mng.token_check(request, session['email']) and dbMng.manager_check(session['email']):
        rows = dbMng.user_data()
        return render_template("manage.html", rows=rows)
    return redirect("/")

#유저 정보 변경 페이지
@app.route("/userinfo", methods=['POST', 'GET'])
def user_info():
    if redis_login_up_mng.token_check(request, session['email']) and dbMng.manager_check(session['email']):
        return render_template("userinfo.html", info=request.args)
        #print(request.form.get('name'))
    return redirect("/")

#유저 정보 변경
@app.route("/changeinfo", methods=['POST', 'GET'])
def change_info():
    if redis_login_up_mng.token_check(request, session['email']) and dbMng.manager_check(session['email']):
        name = request.form.get('name')
        email = request.form.get('email')
        classes = request.form.get('classes')
        print(request.form)
        dbMng.user_info_revise(email, name, classes)
        return redirect("/manage")
    return redirect("/")

#관리자 체크
@app.route("/checkmanager", methods=['POST', 'GET'])
def check_manager():
    if request.method == 'POST':
        email = request.form.get('email')
        if dbMng.manager_check(email):     #관리자면
            return jsonify({
                "manager": "true"
            })
        return jsonify({
            "manager": "false"
        })

#로그아웃kj98
@app.route("/logout")
def logout():
    res = make_response(redirect("/"))
    redis_login_up_mng.delete_session_token(session['email'])
    res.set_cookie("token", '', expires=0)
    session.pop('email', None)
    return res


#이메일 찾은 후에 이메일 전송 -> 인증 후 임시 비밀번호 발급
@app.route("/searchemail", methods=['POST', 'GET'])
def search_email():
    if request.method == 'POST':
        email = request.form.get('email')
        if dbMng.email_exists_check(email):     #이메일 존재시
            key = redis_search_password_mng.create_certification_key(email)     # redis에 세션 넣기
            email_send(key, email, 1)
            return render_template("requestemailcertification.html")
            #인증토큰 만들고 email로 전송 -> redis 저장 -> 클릭시 토큰 비교 -> 비밀번호 변경 창 띄우기 -> 변경
        else:
            error_page(error=None)


#임시 비밀번호 발급
@app.route("/samplepassword", methods=['POST', 'GET'])
def sample_password():
    email = request.args.get('email')
    uuid = request.args.get('uuid')

    # redis의 값과 확인하고 같으면 redis 데이터 지우기
    if redis_search_password_mng.click_url_certification(email, uuid):
        sample_pw = redis_search_password_mng.create_sample_pw()

        dbMng.revise_password(email, sample_pw)
        return render_template('samplepassword.html', password=sample_pw)
    else:
        return error_page(error=None)


#패스워드 변경 페이지
@app.route("/revisepasswordpage")
def revise_password_page():
    return render_template("revisepassword.html")

#패스워드 변경
@app.route("/revisepassword", methods=['POST', 'GET'])
def revise_password():
    if request.method == 'POST':
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')
        if pw1 != pw2 or request.cookies.get('token') != redis_login_up_mng.get_user_uuid(session['email']):
            return jsonify({
                "flag": "false"
            })
        dbMng.revise_password(session['email'], pw1)
        #session.pop('email', None)
        return jsonify({
            "flag": "true"
        })
    return jsonify({
        "flag": "false"
    })


#인증 이메일 전송
# flag = 0 : 회원가입 이메일
# flag = 1 : 비밀번호 찾기 이메일
def email_send(uuid, user_email, flag):
    if flag == 0:
        with app.app_context():
            url = "http://localhost:8082/certification?email=%s&uuid=%s" % (user_email, uuid)
            msg = Message(
                subject="회원가입 인증",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[user_email],  # use your email for testing
                body=url)
            mail.send(msg)
    else:
        with app.app_context():
            url = "http://localhost:8082/samplepassword?email=%s&uuid=%s" % (user_email, uuid)
            msg = Message(
                subject="임시 비밀번호",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[user_email],  # use your email for testing
                body=url)
            mail.send(msg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8082", debug=True)
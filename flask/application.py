from flask import Flask, render_template, redirect, request, jsonify, make_response, Response, session
from flask_mail import Mail, Message
from database.db_manager import DatabaseManger
from database.db_game_manager import GameDataBaseManager
from security.encryption_module import AESCipher
from database.signup_cache_manager import RedisSignUpManager
from database.login_cache_manager import RedisLoginManager
from database.search_password_cache_manager import RedisSearchPasswordManager
from module import game_login_module, sign_up_module, password_module, page_module, game_api_module, logout_module, manager_module

app = Flask(__name__)

app.register_blueprint(game_login_module.blueprints, url_prefix='')
app.register_blueprint(sign_up_module.blueprints, url_prefix='')
app.register_blueprint(password_module.blueprints, url_prefix='')
app.register_blueprint(page_module.blueprints, url_prefix='')
app.register_blueprint(game_api_module.blueprints, url_prefix='')
app.register_blueprint(logout_module.blueprints, url_prefix='')
app.register_blueprint(manager_module.blueprints, url_prefix='')
app.secret_key = b'1234wqerasdfzxcv'
# 페이지 캐시 관리
@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# 에러 처리
@app.errorhandler(404)
def error_page(error):
    print(request.path)
    return render_template("error.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8082", debug=True)

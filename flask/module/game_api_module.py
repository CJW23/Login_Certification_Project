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

blueprints = Blueprint('game_api', __name__)

# 로비에 표현될 데이터
@blueprints.route("/get-data", methods=['POST', 'GET'])
def get_user():
    if request.method == 'POST':
        data = db_game_mng.get_user_data(request.form.get('id'))
        print(data)
        return jsonify({
            "achievescore": data['achievescore'],
            "victory": data['victory'],
            "lose": data['lose'],
            "kill": data['kill'],
            "death": data['death'],
            "damage": data['damage']
        })

# 모든 업적 리스트
@blueprints.route("/get-achieve-data", methods=['POST', 'GET'])
def get_achieve_data():
    data = db_game_mng.get_achievement()
    return jsonify(data)

# 유저가 달성한 업적 리스트
@blueprints.route("/get-user-achieve-data", methods=['POST', 'GET'])
def get_user_achieve_data():
    if request.method == 'POST':
        data = db_game_mng.get_user_achievement(request.form.get('id'))
        return jsonify(data)

# 유저가 달성한 업적 리스트
@blueprints.route("/testtest", methods=['POST', 'GET'])
def testest():
    return jsonify({
        "id": 1,
        "listid": 2,
        "achieve": 'lose'
    })

# 게임이 끝나고 달성 업적 업데이트후 업적 점수 업데이트
@blueprints.route("/update-user-achieve", methods=['POST', 'GET'])
def update_user_achieve():
    game_data = []
    if request.method == 'POST':
        game_data.append(request.form.get('kill'))
        game_data.append(request.form.get('death'))
        game_data.append(request.form.get('damage'))
        print("kill" + str(game_data[0]) + "death" + str(game_data[1]) + "damage" + str(game_data[2]))
        db_game_mng.update_achieve(request.form.get('id'), game_data)
        print("id" + str(request.form.get('id')))
        db_game_mng.update_achieve_score(request.form.get('id'))
        return "true"
    return "false"

# 게임 이긴후 승리 데이터 증가
@blueprints.route("/update-user-victory", methods=['POST', 'GET'])
def update_victory():
    if request.method == 'POST':
        print("승리 아이디" + str(request.form.get('id')))
        db_game_mng.victory_update(request.form.get('id'))
        return "true"
    return "false"

# 게임 패배후 패배 데이터 증가
@blueprints.route("/update-user-lose", methods=['POST', 'GET'])
def update_lose():
    if request.method == 'POST':
        print("패배 아이디" + str(request.form.get('id')))
        db_game_mng.lose_update(request.form.get('id'))
        return "true"
    return "false"

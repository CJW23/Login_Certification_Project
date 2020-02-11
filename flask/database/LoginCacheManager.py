import redis, uuid, datetime
from database.dbManger import DatabaseManger


class RedisLoginManager:
    def __init__(self):
        self.r = redis.Redis(host="127.0.0.1", port=6379, db=1)
        self.db = DatabaseManger()

    #로그인시 세션 토큰 redis set
    def insert_uuid_cookie(self, email):
        token = uuid.uuid4()
        self.r.set(email, str(token), datetime.timedelta(seconds=1800))
        return token

    #토큰 유효시간 체크
    def token_check(self, request, email):
        # token 존재하고 레디스에도 존재하고 uuid값이 같은 경우

        if "token" in request.cookies and self.r.exists(email) > 0 and \
                self.r.get(email).decode('utf-8') == request.cookies.get('token'):
            print("emaiol : " + email)
            return True
        return False

    # redis에 들은 이메일 반환
    def get_user_uuid(self, email):
        return self.r.get(email).decode('utf-8')

    # API 호출때마다 expire 시간 초기화
    def reset_expire(self, request, email):
        token = request.cookies.get('token')
        self.r.set(email, str(token), datetime.timedelta(seconds=1800))

    #로그아웃 레디스 데이터 지우기
    def delete_session_token(self, email):
        self.r.delete(email)

    def token_exists(self, email):
        if self.r.exists(email) > 0:
            return True
        return False
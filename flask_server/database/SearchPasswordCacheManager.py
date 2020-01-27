import redis, uuid, datetime
import string
import random


class RedisSearchPasswordManager:
    def __init__(self):
        self.r = redis.Redis(host="127.0.0.1", port=6379, db=2)

    #인증 키 생성 및 저장
    def create_certification_key(self, email):
        key = uuid.uuid4()
        #같은 이메일이 있는지 체크
        if self.r.exists(email) > 0:
            self.r.delete(email)
            # key, value 데이터 삽입
            self.r.set(email, str(key), datetime.timedelta(seconds=3600))
        else:
            self.r.set(email, str(key), datetime.timedelta(seconds=3600))
        return key

    def create_sample_pw(self):
        lower_upper_alphabet = string.ascii_letters
        random_letter = ''
        for i in range(0, 9):
            random_letter += random.choice(lower_upper_alphabet)
        return random_letter

    # url클릭시 redis 데이터를 1로 바꿔줌.
    def click_url_certification(self, email, uuid):
        if self.r.exists(email) == 1:
            if self.r.get(email).decode('utf8') == uuid:
                self.r.delete(email)
                return True
            else:
                return False
        return False


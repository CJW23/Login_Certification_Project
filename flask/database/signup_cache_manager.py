import redis, uuid, datetime
import time


class RedisSignUpManager:
    def __init__(self):
        self.r = redis.Redis(host="127.0.0.1", port=6379, db=0)

    #인증 키 생성 및 저장
    def create_certification_key(self, email):
        key = uuid.uuid4()
        #같은 이메일이 있는지 체크
        if self.r.exists(email) > 0:
            self.r.delete(email)
            # key, value 데이터 삽입
            self.r.set(email, str(key), datetime.timedelta(seconds=180))
        else:
            self.r.set(email, str(key), datetime.timedelta(seconds=180))
        return key

    def check_certification_key(self, email):
        if self.r.exists(email) == 0:       #redis에 이메일 존재 안할 시
            print(email)
            return "error"

        sec = 5
        while sec < 180:
            print("check")
            if self.r.get(email).decode('utf-8') == '1':
                print("인증 완료")
                return True
            time.sleep(5)
            sec += 5
        return False

    #url클릭시 redis 데이터를 1로 바꿔줌.
    def click_url_certification(self, email, uuid):
        print("get : " + str(self.r.get(email)))
        if self.r.get(email).decode('utf8') == uuid:
            self.r.set(email, 1, datetime.timedelta(seconds=20))
            return True
        else:
            return False

#r = redis.Redis(host="127.0.0.1", port=6379, db=0)
#r.set('b', 'b', datetime.timedelta(seconds=10))
#r.delete('123')
#print(r.exists('123'))

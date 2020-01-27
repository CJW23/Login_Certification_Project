from database.dbModule import Database
from security.encryptionModule import AESCipher
encrypt = AESCipher()


class DatabaseManger:
    def __init__(self):
        self.db = Database()

    #회원 정보 삽입
    def insert_certification(self, param):
        pw = encrypt.extract_password(encrypt.encrypt(param['password']))

        # 유저 정보 삽입
        sql = "INSERT INTO user (useremail, pw, username, salt) VALUES('%s', '%s', '%s', '%s')" % (
            param['email'],
            pw[0],
            param['name'],
            pw[1])

        self.db.execute(sql)
        self.db.commit()

    #이메일 중복 체크
    def email_overlap_check(self, email):
        sql = "SELECT COUNT(useremail) as cnt " \
              "FROM user " \
              "WHERE useremail='%s'" % email
        row = self.db.executeOne(sql)

        if row['cnt'] == 0:
            return True
        return False

    #이메일 존재 여부 체크
    def email_exists_check(self, email):
        sql ="SELECT COUNT(useremail) as cnt " \
             "FROM user " \
             "WHERE useremail='%s'" % email
        row = self.db.executeOne(sql)

        if row['cnt'] == 1:
            return True
        return False

    #로그인 이메일, 비밀번호 체크
    def login_check(self, email, password):
        sql = "SELECT pw, salt " \
              "FROM user " \
              "WHERE useremail='%s'" % email
        row = self.db.executeOne(sql)

        if row is not None:
            pw = encrypt.decrypt(encrypt.origin_password(row['pw'], row['salt']))
            if pw == password:
                return True
        return False

    #관리자 확인
    def manager_check(self, email):
        sql = "SELECT COUNT(1) as cnt " \
              "FROM user " \
              "WHERE useremail='%s' AND manager=1" % email
        row = self.db.executeOne(sql)
        if row['cnt'] == 1:
            return True
        return False

    #유저 데이터 가져오기
    def user_data(self):
        sql = "SELECT useremail, username " \
              "FROM user " \
              "WHERE manager=0"
        return self.db.executeAll(sql)

    #유저 데이터 수정
    def user_info_revise(self, email, name, classes):
        print("설마 : "+str(email))
        sql = "UPDATE user " \
              "SET username='%s', manager=%s " \
              "WHERE useremail='%s'" % (name, classes, email)
        self.db.execute(sql)
        self.db.commit()

    #유저 비밀번호로 데이터 변경
    def revise_password(self, email, pw):
        pw = encrypt.extract_password(encrypt.encrypt(pw))
        sql = "UPDATE user " \
              "SET pw='%s', salt='%s'" \
              "WHERE useremail='%s'" % (pw[0], pw[1], email)
        self.db.execute(sql)
        self.db.commit()

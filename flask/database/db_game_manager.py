from database.db_module import Database

LIST_NUM = 3


class GameDataBaseManager:
    def __init__(self):
        self.db = Database()

    # 로비에서 유저 데이터 가져오기
    # 0: achievescore 1: victory 2: lose
    def get_user_data(self, id):
        data = {}
        sql = "SELECT achievescore, victory, lose, imageid " \
              "FROM user " \
              "WHERE id = %s" % id
        rows = self.db.executeOne(sql)
        data['achievescore'] = rows['achievescore']
        data['victory'] = rows['victory']
        data['lose'] = rows['lose']
        data['imageid'] = rows['imageid']

        sql = "SELECT achievename, val " \
              "FROM user, achievement " \
              "WHERE user.id = %s" % id
        rows = self.db.executeAll(sql)

        # achievename val 가져옴
        for row in rows:
            data[row['achievename']] = row['val']
        return data

    # 업적 리스트
    def get_achievement(self):
        sql = "SELECT id, listid, achieve " \
              "FROM achievementlist;"
        rows = self.db.executeAll(sql)
        return rows

    # 유저가 달성한 업적 리스트
    def get_user_achievement(self, id):
        sql = "SELECT achievementlist.id as id, achievementlist.listid as listid, achievementlist.achieve as achieve " \
              "FROM user, achievement, achievementlist " \
              "WHERE achievement.val >= achievementlist.tskval AND " \
              "user.id = achievement.userid AND " \
              "achievement.achieveid = achievementlist.id AND " \
              "user.id = %s;" % id
        rows = self.db.executeAll(sql)
        return rows

    # 로비에서 유저 접속시 마지막 접속 시간 업데이트
    def update_last_connect(self, id):
        sql = "UPDATE user " \
              "SET lastconnect = NOW() " \
              "WHERE id = %s" % id
        self.db.execute(sql)
        self.db.commit()

    # 게임 승리시 데이터 업데이트
    def victory_update(self, id):
        sql = "UPDATE user " \
              "SET victory = victory + 1 " \
              "WHERE user.id = %s" % id
        self.db.execute(sql)
        self.db.commit()

    # 게임 패배시 데이터 업데이트
    def lose_update(self, id):
        sql = "UPDATE user " \
              "SET lose = lose + 1 " \
              "WHERE user.id = %s" % id
        self.db.execute(sql)
        self.db.commit()

    # 게임이 끝나고 유저의 각각의 새로 달성된 업적 리스트
    def select_achieve(self, id, data):
        for idx in range(0, LIST_NUM):
            sql = "SELECT achievementlist.id, achievementlist.listid, achievementlist.achieve, achievementlist.point " \
                  "FROM user, achievement, achievementlist " \
                  "WHERE achievement.val < achievementlist.tskval AND " \
                  "achievement.val + %s >= achievementlist.tskval AND " \
                  "user.id = achievement.userid AND " \
                  "achievement.achieveid = achievementlist.id " \
                  "AND achievementlist.id = %s " \
                  "AND user.id = %s" % (data[idx], idx, id)
            rows = self.db.executeOne(sql)

    # 게임 종료시 데이터 업데이트
    def update_achieve(self, id, data):
        for idx in range(0, LIST_NUM):
            print("id : " + str(id))
            print(str(idx) + " data : " + str(data[idx]))
            sql = "UPDATE achievement, user " \
                  "SET val = val + " \
                  "(SELECT * FROM (SELECT COALESCE(SUM(achievementlist.point),0) " \
                  "FROM user, achievement, achievementlist " \
                  "WHERE achievement.val < achievementlist.tskval AND " \
                  "achievement.val + %s >= achievementlist.tskval AND " \
                  "user.id = achievement.userid AND " \
                  "achievement.achieveid = achievementlist.id " \
                  "AND achievementlist.id = %s " \
                  "AND user.id = %s) as sum) " \
                  "WHERE user.id = %s" % (data[idx], idx, id, id)
            self.db.execute(sql)
        self.db.commit()

    # 각 달성한 업적의 포인트를 합산한 score를 업적점수에 업데이트
    def update_achieve_score(self, id):
        sql = "UPDATE user " \
              "SET achievescore = " \
              "(SELECT * FROM (SELECT SUM(val) " \
              "FROM user, achievement " \
              "WHERE user.id = achievement.userid AND " \
              "user.id = %s) as t) " \
              "WHERE user.id = %s" % (id, id)
        self.db.execute(sql)
        self.db.commit()

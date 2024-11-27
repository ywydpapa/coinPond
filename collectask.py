import dotenv
import pyupbit
import os
import pymysql
import schedule
import time


dotenv.load_dotenv()
hostenv = os.getenv("host")
userenv = os.getenv("user")
passwordenv = os.getenv("password")
dbenv = os.getenv("db")
charsetenv = os.getenv("charset")


def getkey(uno):
    global result
    db1 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur1 = db1.cursor()
    try:
        sql = "SELECT apikey1,apikey2 from pondUser WHERE userNo=%s and attrib not like %s"
        cur1.execute(sql,(uno, '%XXX'))
        result = cur1.fetchone()
    except Exception as e:
        print("Key 읽기 에러 ",e)
    finally:
        cur1.close()
        db1.close()
        return result


def getcoinlist(uno):
    global coinlist
    db2 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur2 = db2.cursor()
    try:
        sql = "SELECT DISTINCT bidCoin from tradingSetup WHERE userNo=%s and regDate >= DATE_ADD(now(), INTERVAL -1 MONTH)" #1개월 이내 거래 코인 목록
        cur2.execute(sql,uno)
        result = cur2.fetchall()
        coinlist = []
        for item in result:
            coinlist.append(item[0])
    except Exception as e:
        print("거래코인 목록 읽기 에러 ",e)
    finally:
        cur2.close()
        db2.close()
        return coinlist


def gettradelog(uno):
    global tradelog
    keys = getkey(uno)
    key1 = keys[0]
    key2 = keys[1]
    upbit = pyupbit.Upbit(key1, key2)
    coins = getcoinlist(uno)
    tradelogsum = []
    for coin in coins:
        tradelog = upbit.get_order(coin,state='done')
        tradelogsum.append(tradelog)
    return tradelogsum


def insertLog(uno,ldata01,ldata02,ldata03,ldata04,ldata05,ldata06,ldata07,ldata08,ldata09,ldata10,ldata11,ldata12,ldata13):
    global rows
    db3 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur3 = db3.cursor()
    try:
        sql = ("insert into tradeLogDone (userNo,uuid,side,ord_type,price,market,created_at,volume,remaining_volume,reserved_fee,paid_fee,locked,executed_volume,trades_count)"
               " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        cur3.execute(sql,(uno,ldata01,ldata02,ldata03,ldata04,ldata05,ldata06,ldata07,ldata08,ldata09,ldata10,ldata11,ldata12,ldata13))
        db3.commit()
    except Exception as e:
        print("거래완료 기록 인서트 에러", e)
    finally:
        cur3.close()
        db3.close()


def checkuuid(uuid):
    global rows
    db4 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur4 = db4.cursor()
    try:
        sql = "select count(*) from tradeLogDone where uuid=%s"
        cur4.execute(sql,uuid)
        result = cur4.fetchone()
    except Exception as e:
        print("uuid 조회 에러",e)
    finally:
        cur4.close()
        db4.close()
        return result[0]


def setLog(uno):
    global rows
    db5 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur5 = db5.cursor()
    try:
        traderesults= gettradelog(uno)
        for trade in traderesults:
            for item in trade:
                print(item)
                uuidchk = item["uuid"]
                if checkuuid(uuidchk) != 0:
                    print("이미 존재하는 거래")
                else:
                    if item["side"] == "ask":
                        if item.get("price") is not None:
                            ldata01 = item["uuid"]
                            ldata02 = item["side"]
                            ldata03 = item["ord_type"]
                            ldata04 = item["price"]
                            ldata05 = item["market"]
                            ldata06 = item["created_at"]
                            ldata07 = item["volume"]
                            ldata08 = item["remaining_volume"]
                            ldata09 = item["reserved_fee"]
                            ldata10 = item["paid_fee"]
                            ldata11 = item["locked"]
                            ldata12 = item["executed_volume"]
                            ldata13 = item["trades_count"]
                            insertLog(uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09, ldata10, ldata11,ldata12, ldata13)
                    else:
                        print("매수거래 패스")
    except Exception as e:
        print("거래 기록 에러 ",e, "사용자 :", uno)
    finally:
        cur5.close()
        db5.close()


def userlist():
    global rows
    db6 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur6 = db6.cursor()
    try:
        sql = "select userNo from pondUser where apiKey1 is not null"
        cur6.execute(sql)
        rows = cur6.fetchall()
    except Exception as e:
        print("사용자 조회 에러",e)
    finally:
        cur6.close()
        db6.close()
        return rows


def runmain():
    try:
        users = userlist()
        for user in users:
            setLog(user)
            time.sleep(10) #10초 대기 후 실행
    except Exception as e:
        print("자동 반복 실행 에러",e)
    finally:
        return True

schedule.every(10).minutes.do(runmain)


while True:
    schedule.run_pending()
    time.sleep(1)
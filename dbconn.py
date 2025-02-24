import os
import pyupbit
import time
from datetime import datetime
import pymysql
import random
import pandas as pd
import dotenv

dotenv.load_dotenv()
hostenv = os.getenv("host")
userenv = os.getenv("user")
passwordenv = os.getenv("password")
dbenv = os.getenv("db")
charsetenv = os.getenv("charset")

db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
serviceNo = 250204


def getmsetup(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur13 = db.cursor()
    try:
        sql = "select * from tradingSetup where userNo=%s and attrib not like %s"
        cur13.execute(sql, (uno, '%XXXUP'))
        data = list(cur13.fetchall())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur13.close()
        db.close()


def getmsetup_tr(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur13 = db.cursor()
    try:
        sql = "select * from traceSetup where userNo=%s and attrib not like %s"
        cur13.execute(sql, (uno, '%XXXUP'))
        data = list(cur13.fetchall())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur13.close()
        db.close()


def getseton():
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur15 = db.cursor()
    data = []
    print("GetKey !!")
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s"
        cur15.execute(sql, '%XXXUP')
        data = cur15.fetchall()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur15.close()
        db.close()


def getsetonsvr(svrNo):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur16 = db.cursor()
    data = []
    try:
        sql = "SELECT distinct userNo from tradingSetup where attrib not like %s and serverNo=%s"
        cur16.execute(sql, ('%XXXUP', svrNo))
        data = cur16.fetchall()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur16.close()
        db.close()


def getsetonsvr_tr(svrNo):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur16 = db.cursor()
    data = []
    try:
        sql = "SELECT distinct userNo from traceSetup where attrib not like %s and serverNo=%s"
        cur16.execute(sql, ('%XXXUP', svrNo))
        data = cur16.fetchall()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur16.close()
        db.close()


def getupbitkey(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur17 = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE userNo=%s and attrib not like %s"
        cur17.execute(sql, (uno, '%XXXUP'))
        data = cur17.fetchone()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur17.close()
        db.close()


def getupbitkey_tr(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur17 = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM traceUser WHERE userNo=%s and attrib not like %s"
        cur17.execute(sql, (uno, '%XXXUP'))
        data = cur17.fetchone()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur17.close()
        db.close()


def getupbitkey_tr(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur17 = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM traceUser WHERE userNo=%s and attrib not like %s"
        cur17.execute(sql, (uno, '%XXXUP'))
        data = cur17.fetchone()
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur17.close()
        db.close()


def clearcache():
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur18 = db.cursor()
    sql = "RESET QUERY CACHE"
    cur18.execute(sql)
    cur18.close()
    db.close()


def setdetail(setno):
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur20 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE setNo = %s"
        cur20.execute(sql, setno)
        rows = cur20.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur20.close()
        db.close()
    return rows


def setdetail_tr(setno):
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur20 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM traceSets WHERE setNo = %s"
        cur20.execute(sql, setno)
        rows = cur20.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur20.close()
        db.close()
    return rows


def errlog(err, userno):
    global rows
    db28 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur28 = db28.cursor()
    try:
        sql = "INSERT INTO error_Log (error_detail, userNo) VALUES (%s, %s)"
        cur28.execute(sql, (err, userno))
        db28.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur28.close()
        db28.close()


def servicelog(log, userno):
    global rows
    db30 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur30 = db30.cursor()
    try:
        sql = "INSERT INTO service_Log (service_detail, userNo) VALUES (%s, %s)"
        cur30.execute(sql, (log, userno))
        db30.commit()
    except Exception as e:
        print('접속오류 서비스로그', e)
    finally:
        cur30.close()
        db30.close()


def tradelog(uno, type, coinn, tstamp):
    global rows
    db32 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur32 = db32.cursor()
    try:
        if tstamp == "":
            tstamp = datetime.now()
        sql = "INSERT INTO tradeLog (userNo, tradeType, coinName, regDate) VALUES (%s, %s, %s, %s)"
        cur32.execute(sql, (uno, type, coinn, tstamp))
        db32.commit()
    except Exception as e:
        print('트레이드 로그실행 오류', e)
    finally:
        cur32.close()
        db32.close()


def getlog(uno, type, coinn):
    global rows
    db33 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur33 = db33.cursor()
    try:
        sql = "SELECT regDate FROM tradeLog where userNo = %s and attrib = %s and tradeType = %s and coinName = %s"
        cur33.execute(sql, (uno, '100001000010000', type, coinn))
        rows = cur33.fetchone()
    except Exception as e:
        print("트레이드 로그 조회 오류 ", e)
    finally:
        cur33.close()
        db33.close()
        return rows


def modifyLog(uuid, stat):
    global rows
    db34 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur34 = db34.cursor()
    try:
        sql = "UPDATE tradeLogDetail set attrib = %s where uuid = %s"
        if stat == "canceled":
            stat = "CANC0CANC0CANC0"
        elif stat == "confirmed":
            stat = "CONF0CONF0CONF0"
        else:
            stat = "UPD00UPD00UPD00"
        cur34.execute(sql, (stat, uuid))
        db34.commit()
    except Exception as e:
        print('거래 기록 업데이트 에러', e)
    finally:
        cur34.close()
        db34.close()


def insertLog(uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09, ldata10, ldata11,
              ldata12, ldata13, ldata14, ldata15, ldata16):
    global rows
    db35 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur35 = db35.cursor()
    try:
        sql = (
            "insert into tradeLogDetail (userNo,orderDate,uuid,side,ord_type,price,market,created_at,volume,remaining_volume,reserved_fee,paid_fee,locked,executed_volume,excuted_funds,trades_count,time_in_force)"
            " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        cur35.execute(sql, (
        uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09, ldata10, ldata11, ldata12,
        ldata13, ldata14, ldata15, ldata16))
        db35.commit()
    except Exception as e:
        print("거래 기록 인서트 에러", e)
    finally:
        cur35.close()
        db35.close()


def serviceStat(sno, sip, sver):
    global rows
    db36 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur36 = db36.cursor()
    try:
        sql = "INSERT INTO service_Stat (serverNo,serviceIp,serviceVer) VALUES (%s, %s, %s)"
        cur36.execute(sql, (sno, sip, sver))
        db36.commit()
    except Exception as e:
        print('접속상태 Log 기록 에러', e)
    finally:
        cur36.close()
        db36.close()


def getserverType(sno):
    global rows
    db37 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur37 = db37.cursor()
    try:
        sql = "select serviceType, serviceYN from serverSet where serverNo = %s and attrib not like %s"
        cur37.execute(sql, (sno, "XXXUP%"))
        rows = cur37.fetchone()
    except Exception as e:
        print('서버 서비스 조회', e)
    finally:
        cur37.close()
        db37.close()
        return rows


def lclog(coinn, uno, gap, lcamt, mywon, lossamt):
    global rows
    db38 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur38 = db38.cursor()
    try:
        sql = "INSERT INTO lcLog (lcCoinn,userNo,lcGap,lcAmt, remainKrw, lossAmt ) VALUES (%s, %s, %s, %s, %s, %s)"
        cur38.execute(sql, (coinn, uno, gap, lcamt, mywon, lossamt))
        db38.commit()
    except Exception as e:
        print('손절상태 Log 기록 에러', e)
    finally:
        cur38.close()
        db38.close()


def setonoff(sno, yesno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur39 = db.cursor()
    try:
        sql = "UPDATE traceSetup SET activeYN = %s where setupNo=%s"
        cur39.execute(sql, (yesno, sno))
        db.commit()
    except Exception as e:
        print('상태 업데이트 오류', e)
    finally:
        cur39.close()
        db.close()

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
serverNo = 2
serviceNo = 240808


def checkkey(uno, setkey):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur8 = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur8.execute(sql,(setkey, uno, '%XXX'))
    result = cur8.fetchall()
    cur8.close()
    db.close()
    if len(result) == 0:
        print("No match Keys !!")
        return False
    else:
        return True


def erasebid(uno, setkey):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur9 = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur9.execute(sql,(setkey, uno, '%XXX'))
    result = cur9.fetchall()
    if len(result) == 0:
        print("No match Keys !!")
        cur9.close()
        db.close()
        return False
    else:
        sql2 = "update tradingSetup set attrib=%s where userNo=%s"
        cur9.execute(sql2,("XXXUPXXXUPXXXUP", uno))
        db.commit()
        cur9.close()
        db.close()
        return True



def setupbid(uno, setkey, initbid, bidstep, bidrate, askrate, coinn, svrno, tradeset):
    chkkey = checkkey(uno, setkey)
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur0 = db.cursor()
    if chkkey == True:
        try:
            erasebid(uno, setkey)
            sql = "insert into tradingSetup (userNo, initAsset, bidInterval, bidRate, askrate, bidCoin, custKey ,serverNo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cur0.execute(sql, (uno, initbid, bidstep, bidrate, askrate, coinn, tradeset, svrno))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur0.close()
            db.close()
            return True
    else:
        return False


def setupbidadmin(uno, setkey, settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9):
    chkkey = checkkey(uno, setkey)
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur11 = db.cursor()
    if chkkey == True:
        try:
            sql = ("insert into tradingSets (setTitle, setInterval, step0, step1, step2, step3, step4, step5, step6, step7, step8, step9, inter0, inter1, inter2, inter3, inter4, inter5, inter6, inter7, inter8, inter9, regdate) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())")
            cur11.execute(sql, (settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8,int9, ))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur11.close()
            db.close()
            return True
    else:
        return False


def getsetup(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur12 = db.cursor()
    try:
        sql = "SELECT bidCoin, initAsset, bidInterval, bidRate, askRate, activeYN, custKey from tradingSetup where userNo=%s and attrib not like %s"
        cur12.execute(sql, (uno, '%XXXUP'))
        data = list(cur12.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur12.close()
        db.close()


def getsetups(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur13 = db.cursor()
    try:
        sql = "select * from tradingSetup where userNo=%s and attrib not like %s"
        cur13.execute(sql, (uno, '%XXXUP'))
        data = list(cur13.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur13.close()
        db.close()


def setonoff(uno,yesno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur14 = db.cursor()
    try:
        sql = "UPDATE tradingSetup SET activeYN = %s where userNo=%s AND attrib not like %s"
        cur14.execute(sql, (yesno, uno,'%XXXUP'))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur14.close()
        db.close()


def getseton():
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur15 = db.cursor()
    data = []
    print("GetKey !!")
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s"
        cur15.execute(sql,'%XXXUP')
        data = cur15.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur15.close()
        db.close()


def getsetonsvr(svrNo):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur16 = db.cursor()
    data = []
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s and serverNo=%s"
        cur16.execute(sql,('%XXXUP', svrNo))
        data = cur16.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur16.close()
        db.close()


def getupbitkey(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur17 = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE userNo=%s and attrib not like %s"
        cur17.execute(sql, (uno,'%XXXUP'))
        data = cur17.fetchone()
        return data
    except Exception as e:
        print('접속오류',e)
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


def errlog(err,userno):
    global rows
    db28 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur28 = db28.cursor()
    try:
        sql = "INSERT INTO error_Log (error_detail, userNo) VALUES (%s, %s)"
        cur28.execute(sql,(err, userno))
        db28.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur28.close()
        db28.close()


def setholdYN(setno, yn):
    global rows
    db29 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur29 = db29.cursor()
    try:
        sql = "UPDATE tradingSetup set holdYN = %s where setupNo = %s"
        cur29.execute(sql, (yn, setno))
        db29.commit()
    except Exception as e:
        print('접속오류 에러로그', e)
    finally:
        cur29.close()
        db29.close()


def servicelog(log,userno):
    global rows
    db30 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur30 = db30.cursor()
    try:
        sql = "INSERT INTO service_Log (service_detail, userNo) VALUES (%s, %s)"
        cur30.execute(sql,(log,userno))
        db30.commit()
    except Exception as e:
        print('접속오류 서비스로그', e)
    finally:
        cur30.close()
        db30.close()


def getSignal(coinn):
    global rows
    db31 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur31 = db31.cursor()
    try:
        sql = "SELECT * FROM trendSignal WHERE coinName=%s and attrib NOT LIKE %s"
        cur31.execute(sql, (coinn, "UPD00%"))
        rows = cur31.fetchone()
    except Exception as e:
        print("코인 트렌드 조회 에러 : ",e)
    finally:
        cur31.close()
        db31.close()
        return rows


def tradelog(uno,type,coinn,tstamp):
    global rows
    db32 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur32 = db32.cursor()
    try:
        if tstamp == "":
            tstamp = datetime.now()
        sql = "update tradeLog set attrib = %s where userNo = %s and tradeType = %s"
        cur32.execute(sql, ("UPD00UPD00UPD00", uno, type))
        sql = "INSERT INTO tradeLog (userNo, tradeType, coinName, regDate) VALUES (%s, %s, %s, %s)"
        cur32.execute(sql,(uno, type, coinn, tstamp))
        db32.commit()
    except Exception as e:
        print('접속오류 트레이드 로그', e)
    finally:
        cur32.close()
        db32.close()


def getlog(uno,type,coinn):
    global rows
    db33= pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur33= db33.cursor()
    try:
        sql = "SELECT regDate FROM tradeLog where userNo = %s and attrib = %s and tradeType = %s and coinName = %s"
        cur33.execute(sql, (uno,'100001000010000' ,type, coinn))
        rows = cur33.fetchone()
    except Exception as e:
        print("트레이드 로그 조회 오류 ", e)
    finally:
        cur33.close()
        db33.close()
        return rows




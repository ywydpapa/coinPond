import pyupbit
import time
from datetime import datetime
import pymysql
import random
import pandas as pd


db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
serverNo = 2


def check_srv(coinn, perc):
    values = pyupbit.get_ohlcv(coinn, interval="hour", count=48)
    volumes = values['volume']
    if len(volumes) < 21:
        return False
    sum_vol20 = 0
    today_vol = 0
    for i, vol in enumerate(volumes):
        if i == 0:
            today_vol = vol
        elif 1 <= i <= 20:
            sum_vol20 += vol
        else:
            break
    avg_vol20 = sum_vol20 / 20
    if today_vol > avg_vol20 * perc:
        return True


def selectUsers(uid, upw):
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur1 = db.cursor()
    row = None
    setkey = None
    try:
        sql = "SELECT userNo, userName, serverNo, userRole FROM pondUser WHERE userPasswd=password(%s) AND userId=%s AND attrib NOT LIKE %s"
        cur1.execute(sql, (upw, uid, str("%XXX")))
        row = cur1.fetchone()
        print(row)
        if row is not None:
            setkey = random.randint(100000,999999)
    except Exception as e:
        print('접속오류', e)
    finally:
        cur1.close()
        db.close()
    return row, setkey


def listUsers():
    global rows
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur2 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE attrib NOT LIKE %s"
        cur2.execute(sql, str("%XXX"))
        rows = cur2.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur2.close()
        db.close()
    return rows


def detailuser(uno):
    global rows
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur3 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE userNo = %s and attrib NOT LIKE %s"
        cur3.execute(sql, (uno,str("%XXX")))
        rows = cur3.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur3.close()
        db.close()
    return rows


def setKeys(uno, setkey):
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur4 = db.cursor()
    try:
        sql = "UPDATE pondUser SET setupKey = %s, lastLogin = now() where userNo=%s"
        cur4.execute(sql, (setkey, uno))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur4.close()
        db.close()


def check_srv(coinn,perc):
    values = pyupbit.get_ohlcv(coinn, interval="day", count=30)
    volumes = values['volume']
    if len(volumes) < 21:
        return False
    sum_vol20 = 0
    today_vol = 0
    for i, vol in enumerate(volumes):
        if i == 0:
            today_vol = vol
        elif 1 <= i <= 20:
            sum_vol20 += vol
        else:
            break
    avg_vol20 = sum_vol20 / 20
    if today_vol > avg_vol20 * perc:
        return True


def checkwallet(uno, setkey):
    global key1, key2, walletitems
    walletitems = []
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur5 = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur5.execute(sql,(setkey, uno, '%XXX'))
    keys = cur5.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        walletitems = upbit.get_balances()
        print(walletitems)
    cur5.close()
    db.close()
    return walletitems


def checkwalletwon(uno, setkey):
    global key1, key2, walletwon
    walletwon = []
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur6 = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur6.execute(sql,(setkey, uno, '%XXX'))
    keys = cur6.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        walletwon = round(upbit.get_balance("KRW"))
    cur6.close()
    db.close()
    return walletwon


def tradehistory(uno, setkey):
    tradelist = []
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur7 = db.cursor()
    sql = "SELECT bidCoin from tradingSetup where userNo = %s and attrib not like %s "
    cur7.execute(sql,(uno, '%XXXUP'))
    data = cur7.fetchone()
    coinn = data[0]
    sql2 = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur7.execute(sql2,(setkey, uno, '%XXX'))
    keys = cur7.fetchone()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0]
        key2 = keys[1]
        upbit = pyupbit.Upbit(key1,key2)
        tradelist = upbit.get_order(coinn,state='done')
    cur7.close()
    db.close()
    return tradelist


def checkkey(uno, setkey):
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    if chkkey == True:
        try:
            erasebid(uno, setkey)
            db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',  charset='utf8')
            cur0 = db.cursor()
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
    if chkkey == True:
        try:
            db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',
                                 charset='utf8')
            cur11 = db.cursor()
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
    try:
        db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',
                             charset='utf8')
        cur12 = db.cursor()
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
    try:
        db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',
                             charset='utf8')
        cur13 = db.cursor()
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur18 = db.cursor()
    sql = "RESET QUERY CACHE"
    cur18.execute(sql)
    cur18.close()
    db.close()


def getorderlist(uno):
    keys = getupbitkey(uno)
    setups = getsetup(uno)
    coinn = setups[0]
    upbit = pyupbit.Upbit(keys[0],keys[1])
    orders = upbit.get_order(coinn)
    return orders


def sellmycoin(uno,coinn):
    keys = getupbitkey(uno)
    upbit = pyupbit.Upbit(keys[0],keys[1])
    walt = upbit.get_balances()
    print(coinn)
    for coin in walt:
        if coin['currency'] == coinn:
            balance = float(coin['balance'])
            coinn = "KRW-"+ coinn
            result = upbit.sell_market_order(coinn,balance)
            try:
                if result["error"]["name"] == 'under_min_total_market_ask':
                    buy5000 = upbit.buy_market_order(coinn, 5000)
                    print(buy5000)
            except Exception as e:
                pass
        else:
            pass


def selectsets():
    global rows
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur19 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE attrib NOT LIKE %s"
        cur19.execute(sql, str("%XXX"))
        rows = cur19.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur19.close()
        db.close()
    return rows


def setdetail(setno):
    global rows
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
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

def selectsetlist(sint):
    global rows
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur21 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE useYN = %s and attrib NOT LIKE %s"
        if sint > 0:
            useyn = 'Y'
        cur21.execute(sql, (useyn, "XXX%"))
        rows = cur21.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur21.close()
        db.close()
    return rows


def setmypasswd(uno, passwd):
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur22 = db.cursor()
    try:
        sql = "UPDATE pondUser SET userPasswd = password(%s) where userNo=%s"
        cur22.execute(sql, (passwd, uno))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur22.close()
        db.close()


def updateuserdetail(uno, key1, key2, svrno):
    db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur23 = db.cursor()
    try:
        sql= "UPDATE pondUser SET apiKey1 = %s, apiKey2 = %s, serverNo = %s where userNo = %s"
        cur23.execute(sql, (key1, key2, svrno, uno))
        db.commit()
    except Exception as e:
        print('사용자 업데이트 오류', e)
    finally:
        cur23.close()
        db.close()


def updatebidadmin(uno, setkey, settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9, setsno):
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        db24 = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',
                             charset='utf8')
        cur24 = db24.cursor()
        try:
            sql = ("UPDATE tradingSets set setTitle = %s, setInterval = %s, step0 = %s, step1 = %s, step2 = %s, step3 = %s, step4 = %s, step5 = %s, step6 = %s, step7 = %s, step8 = %s, step9 = %s, "
                   "inter0 = %s, inter1 = %s, inter2 = %s, inter3 = %s, inter4 = %s, inter5 = %s, inter6 = %s, inter7 = %s, inter8 = %s, inter9 = %s where setNo = %s ")
            cur24.execute(sql, (settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9, setsno))
            db24.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur24.close()
            db24.close()
            return True
    else:
        return False


def settingonoff(sno, yesno):
    db25 = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur25 = db25.cursor()
    try:
        sql = "UPDATE tradingSets SET useYN = %s where setNo=%s"
        cur25.execute(sql, (yesno, sno))
        db25.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur25.close()
        db25.close()


def hotcoinlist():
    global rows
    db26 = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
    cur26 = db26.cursor()
    row = None
    try:
        sql = "SELECT * FROM hotCoins WHERE attrib NOT LIKE %s"
        cur26.execute(sql, "XXX%")
        rows = cur26.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur26.close()
        db26.close()
    return rows


def sethotcoin(coinn):
    global rows
    db27 = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit',
                           charset='utf8')
    cur27 = db27.cursor()
    try:
        sql = "UPDATE hotCoins SET attrib = %s where coinName=%s"
        cur27.execute(sql, ("XXX00XXX00XXX00",coinn))
        db27.commit()
        sql = "INSERT INTO hotCoins (coinName, regDate) VALUES (%s, %s)"
        cur27.execute(sql,(coinn, 'now()'))
        db27.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur27.close()
        db27.close()
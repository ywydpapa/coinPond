from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import dotenv
import os
from datetime import datetime

dotenv.load_dotenv()
DATABASE_URL = os.getenv("dburl")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

serviceNo = 250727

async def getmsetup_tr(uno):
    try:
        async with async_session() as session:
            sql = text("select * from traceSetup where userNo=:uno and attrib not like :attrib")
            result = await session.execute(sql, {"uno": uno, "attrib": "%XXXUP"})
            data = result.fetchall()
            return data
    except Exception as e:
        print('접속오류', e)
        return None

async def getmsetup_tr(uno):
    try:
        async with async_session() as session:
            sql = text("select * from traceSetup where userNo=:uno and attrib not like :xattr")
            result = await session.execute(sql, {"uno":uno, "xattr": '%XXXUP'})
            data = result.fetchall()
            return data
    except Exception as e:
        print('접속오류', e)


async def getseton():
    try:
        async with async_session() as session:
            sql = text("SELECT userNo from tradingSetup where attrib not like :xattr")
            result = await session.execute(sql, {"xattr":'%XXXUP'})
            data = result.fetchall()
            return data
    except Exception as e:
        print('접속오류', e)


async def getsetonsvr_tr(svrNo):
    try:
        async with async_session() as session:
            sql = text("SELECT distinct userNo from traceSetup where attrib not like :xattr and serverNo=:svrno")
            result = await session.execute(sql, {"xattr":'%XXXUP', "svrno":svrNo})
            data = result.fetchall()
            return data
    except Exception as e:
        print('접속오류', e)


async def getupbitkey_tr(uno):
    try:
        async with async_session() as session:
            sql = text("SELECT apiKey1, apiKey2 FROM traceUser WHERE userNo=:uno and attrib not like :xattr")
            result = await session.execute(sql, {"uno":uno, "xattr":'%XXXUP'})
            data = result.fetchone()
            return data
    except Exception as e:
        print('접속오류', e)


async def clearcache():
    try:
        async with async_session() as session:
            sql = text("RESET QUERY CACHE")
            result = await session.execute(sql)
            return result
    except Exception as e:
        print('Clear Cache Error',e)


async def setdetail_tr(setno):
    try:
        async with async_session() as session:
            sql = text("SELECT * FROM traceSets WHERE setNo = :setno")
            result = await session.execute(sql, {"setno":setno})
            data = result.fetchone()
            return data
    except Exception as e:
        print('접속오류', e)


async def errlog(err, uno):
    try:
        async with async_session() as session:
            sql = text("INSERT INTO error_Log (error_detail, userNo) VALUES (:err, :uno)")
            result = await session.execute(sql, {"err": err, "uno": uno})
            await session.commit()
            return True
    except Exception as e:
        print('접속오류', e)


async def servicelog(log, uno):
    try:
        async with async_session() as session:
            sql = text("INSERT INTO service_Log (service_detail, userNo) VALUES (:log, :uno)")
            result = await session.execute(sql, {"log": log, "uno": uno})
            await session.commit()
            return True
    except Exception as e:
        print('접속오류 서비스로그', e)


async def tradelog(uno, type, coinn, tstamp):
    try:
        async with async_session() as session:
            if tstamp == "":
                tstamp = datetime.now()
                tstamp = tstamp.strftime("%Y-%m-%d %H:%M:%S")
            sql = text("INSERT INTO tradeLog (userNo, tradeType, coinName, regDate) VALUES (:uno, :type, :coinn, :tstamp)")
            result = await session.execute(sql, {"uno": uno, "type": type, "coinn": coinn, "tstamp": tstamp})
            await session.commit()
            return True
    except Exception as e:
        print('트레이드 로그실행 오류', e)


async def getlog(uno, type, coinn):
    try:
        async with async_session() as session:
            sql = text("SELECT regDate FROM tradeLog where userNo = :uno and attrib = :attr and tradeType = :type and coinName = :coinn")
            result = await session.execute(sql, {"uno": uno, "attr": "100001000010000", "type": type, "coinn": coinn})
            data = result.fetchone()
            return data
    except Exception as e:
        print("트레이드 로그 조회 오류 ", e)


async def modifyLog(uuid, stat):
    try:
        async with async_session() as session:
            if stat == "canceled":
                stat = "CANC0CANC0CANC0"
            elif stat == "confirmed":
                stat = "CONF0CONF0CONF0"
            else:
                stat = "UPD00UPD00UPD00"
            sql = text("UPDATE tradeLogDetail set attrib = :attr where uuid = :uuid")
            result = await session.execute(sql, {"attr": stat, "uuid": uuid})
            await session.commit()
            return True
    except Exception as e:
        print('거래 기록 업데이트 에러', e)


async def insertLog(uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09, ldata10, ldata11,
              ldata12, ldata13, ldata14, ldata15, ldata16):
    try:
        async with async_session() as session:
            sql = text("""
                INSERT INTO tradeLogDetail (
                    userNo, orderDate, uuid, side, ord_type, price, market, created_at, volume, 
                    remaining_volume, reserved_fee, paid_fee, locked, executed_volume, excuted_funds, trades_count, time_in_force
                )
                VALUES (
                    :uno, :ldata01, :ldata02, :ldata03, :ldata04, :ldata05, :ldata06, :ldata07, :ldata08, 
                    :ldata09, :ldata10, :ldata11, :ldata12, :ldata13, :ldata14, :ldata15, :ldata16
                )
            """)
            params = {
                "uno": uno,
                "ldata01": ldata01,
                "ldata02": ldata02,
                "ldata03": ldata03,
                "ldata04": ldata04,
                "ldata05": ldata05,
                "ldata06": ldata06,
                "ldata07": ldata07,
                "ldata08": ldata08,
                "ldata09": ldata09,
                "ldata10": ldata10,
                "ldata11": ldata11,
                "ldata12": ldata12,
                "ldata13": ldata13,
                "ldata14": ldata14,
                "ldata15": ldata15,
                "ldata16": ldata16
            }
            await session.execute(sql, params)
            await session.commit()
            return True
    except Exception as e:
        print("거래 기록 인서트 에러", e)
        return False


async def serviceStat(sno, sip, sver):
    try:
        async with async_session() as session:
            sql = text("INSERT INTO service_Stat (serverNo,serviceIp,serviceVer) VALUES (:sno, :sip, :sver)")
            result = await session.execute(sql, {"sno":sno, "sip":sip, "sver":sver})
            await session.commit()
            return True
    except Exception as e:
        print('접속상태 Log 기록 에러', e)


async def getserverType(sno):
    try:
        async with async_session() as session:
            sql = text("select serviceType, serviceYN from serverSet where serverNo = :sno and attrib not like :xattr")
            result = await session.execute(sql, {"sno":sno,"xattr":"%XXXUP%"})
            data = result.fetchone()
            return data
    except Exception as e:
        print('서버 서비스 조회', e)


async def lclog(coinn, uno, gap, lcamt, mywon, lossamt):
    try:
        async with async_session() as session:
            sql = text("INSERT INTO lcLog (lcCoinn,userNo,lcGap,lcAmt, remainKrw, lossAmt ) VALUES (:coinn, :uno, :gap, :lcamt, :mywon, :lossamt)")
            result = await session.execute(sql, {"coinn":coinn,"uno": uno, "gap":gap, "lcamt":lcamt, "mywon":mywon, "lossamt":lossamt})
            await session.commit()
            return True
    except Exception as e:
        print('손절상태 Log 기록 에러', e)


async def setonoff(sno, yesno):
    try:
        async with async_session() as session:
            sql = text("UPDATE traceSetup SET activeYN = :yesno where setupNo=:sno")
            result = await session.execute(sql, {"yesno":yesno, "sno":sno})
            await session.commit()
            return True
    except Exception as e:
        print('상태 업데이트 오류', e)

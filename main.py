import time
from contextlib import nullcontext
from datetime import datetime
from pyupbit import Upbit
import dbconn
import pyupbit
import dotenv
import os
import sys
import requests

from dbconn import tradelog, setdetail

dotenv.load_dotenv()
bidcnt = 1
svrno = os.getenv("server_no")
mainver = 241101001


def loadmyset(uno):
    global mysett
    try:
        mysett = dbconn.getsetups(uno)
    except Exception as e:
        msg = "나의 세팅 조회 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return mysett


def buymarketpr(key1, key2, coinn, camount, uno):
    global orders
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.buy_market_order(coinn, camount)
    except Exception as e:
        msg = "시장가 구매 명령 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return orders


def buylimitpr(key1, key2, coinn, setpr, setvol, uno):
    global orders
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.buy_limit_order(coinn, setpr, setvol)
    except Exception as e:
        msg = "지정가 구매 명령 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return orders


def selllimitpr(key1, key2, coinn, setpr, setvol, uno):
    global orders
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.sell_limit_order(coinn, setpr, setvol)
        print(orders)
        if orders is not None:
            ldata01 = datetime.now()
            ldata02 = orders["uuid"]
            ldata03 = orders["side"]
            ldata04 = orders["ord_type"]
            ldata05 = orders["price"]
            ldata06 = orders["market"]
            ldata07 = orders["created_at"]
            ldata08 = orders["volume"]
            ldata09 = orders["remaining_volume"]
            ldata10 = orders["reserved_fee"]
            ldata11 = orders["paid_fee"]
            ldata12 = orders["locked"]
            ldata13 = float(orders["executed_volume"])
            ldata14 = float(0)
            ldata15 = "0"
            ldata16 = "0"
            dbconn.insertLog(uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09, ldata10, ldata11, ldata12, ldata13, ldata14, ldata15, ldata16)
    except Exception as e:
        msg = "지정가 매도 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return orders


def checktraded(key1, key2, coinn, uno):
    try:
        upbit = pyupbit.Upbit(key1, key2)
        checktrad = upbit.get_balances()
        if checktrad is None:
            pass
        for wallet in checktrad:
            if "KRW-" + wallet['currency'] == coinn:
                if float(wallet['balance']) != 0.0:
                    print("잔고 남아 재거래 실행 설정")
                else:
                    print('매도 거래 대기중')
                return wallet
            else:
                pass
    except Exception as e:
        msg = "잔고 확인 에러 " + str(e)
        send_error(msg, uno)


def calprice(bidprice, uno):
    try:
        if bidprice >= 2000000:
            bidprice = round(bidprice, -3)
        elif 1000000 <= bidprice < 20000000:
            bidprice = round(bidprice, -3) + 500
        elif 500000 <= bidprice < 1000000:
            bidprice = round(bidprice, -2)
        elif 100000 <= bidprice < 500000:
            bidprice = round(bidprice, -2) + 50
        elif 10000 <= bidprice < 100000:
            bidprice = round(bidprice, -1)
        elif 1000 <= bidprice < 10000:
            bidprice = round(bidprice)
        elif 100 <= bidprice < 1000:
            bidprice = round(bidprice, 1)
        elif 10 <= bidprice < 100:
            bidprice = round(bidprice, 2)
        elif 1 <= bidprice < 10:
            bidprice = round(bidprice, 3)
        else:
            bidprice = round(bidprice, 4)
    except Exception as e:
        msg = "주문 가격 산출 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return bidprice


def calprice2(bidprice, uno):
    try:
        if bidprice >= 2000000:
            bidprice = round(bidprice, -3)
        elif 1000000 <= bidprice < 20000000:
            bidprice = round(bidprice, -3) + 500
        elif 500000 <= bidprice < 1000000:
            bidprice = round(bidprice, -2)
        elif 100000 <= bidprice < 500000:
            bidprice = round(bidprice, -2) + 50
        elif 10000 <= bidprice < 100000:
            bidprice = round(bidprice, -1)
        elif 1000 <= bidprice < 10000:
            bidprice = round(bidprice)
        elif 100 <= bidprice < 1000:
            bidprice = round(bidprice)
        elif 10 <= bidprice < 100:
            bidprice = round(bidprice, 2)
        elif 1 <= bidprice < 10:
            bidprice = round(bidprice, 3)
        else:
            bidprice = round(bidprice, 4)
    except Exception as e:
        msg = "주문 가격 산출 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return bidprice


def cancelaskorder(key1, key2, coinn, uno):  # 매도 주문 취소
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    try:
        if orders is not None:
            for order in orders:
                if order['side'] == 'ask':
                    upbit.cancel_order(order["uuid"])
                    dbconn.modifyLog(order["uuid"],"cancelled")
                else:
                    print("매수 주문 유지")
        else:
            pass
    except Exception as e:
        msg = '매도주문취소 에러 '+str(e)
        send_error(msg, uno)


def canclebidorder(key1, key2, coinn, uno):  # 청산
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    try:
        if orders is not None:
            for order in orders:
                if order['side'] == 'bid':
                    upbit.cancel_order(order["uuid"])
                else:
                    print("매도 주문 유지")
        else:
            pass
    except Exception as e:
        msg = '매수주문취소 에러 :'+ str(e)
        send_error(msg, uno)


def order_mod_ask5(key1, key2, coinn, profit, uno):  #이윤 변동식 계산 방식
    print("매도 주문5 재생성")
    try:
        cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit / 100)
        print("재설정 이윤 :", profit)
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        setprice = calprice(setprice, uno)
        selllimitpr(key1, key2, coinn, setprice, totalvol, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = '매도주문5 갱신 에러 '+str(e)
        send_error(msg, uno)


def get_trend(coinn , uno):
    opoint, cpoint, hpoint, lpoint, vpoint = 0, 0, 0, 0, 0
    trend = []
    try:
        crprice = pyupbit.get_current_price(coinn)
        candls = pyupbit.get_ohlcv(ticker=coinn, interval="minute1", count=4)
        candls = [candls]
        openpr = candls[0]['open'].tolist()
        closepr = candls[0]['close'].tolist()
        highpr = candls[0]['high'].tolist()
        lowpr = candls[0]['low'].tolist()
        volumepr = candls[0]['volume'].tolist()
        opric, cpric, hpric, lpric, volic = [], [], [], [], []
        for i in range(0, 3):
            if openpr[i + 1] > openpr[i]:
                opric.append('+')
                opoint = opoint + 1
            elif openpr[i + 1] <= openpr[i]:
                opric.append('-')
                opoint = opoint - 1
            if closepr[i + 1] > closepr[i]:
                cpric.append('+')
                cpoint = cpoint + 1
            elif closepr[i + 1] <= closepr[i]:
                cpric.append('-')
                cpoint = cpoint - 1
            if highpr[i + 1] > highpr[i]:
                hpric.append('+')
                hpoint = hpoint + 1
            elif highpr[i + 1] <= highpr[i]:
                hpric.append('-')
                hpoint = hpoint - 1
            if lowpr[i + 1] > lowpr[i]:
                lpric.append('+')
                lpoint = lpoint + 1
            elif lowpr[i + 1] <= lowpr[i]:
                lpric.append('-')
                lpoint = lpoint - 1
            if volumepr[i + 1] > volumepr[i]:
                volic.append('+')
                vpoint = vpoint + 1
            elif volumepr[i + 1] <= volumepr[i]:
                volic.append('-')
                vpoint = vpoint - 1
        trend = opric
        trend.extend(cpric)
        trend.extend(hpric)
        trend.extend(lpric)
        trend.extend(volic)
    except Exception as e:
        msg = "트렌드 체크 에러 "+str(e)
        send_error(msg, uno)
    finally:
        return trend, opoint + cpoint + hpoint + lpoint, vpoint


def add_new_bid(key1, key2, coinn, bidprice, bidvol, uno):
    try:
        ret = buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        tradelog(uno,"BID", coinn, datetime.now()) #주문 기록
        return ret
    except Exception as e:
        msg = "추가매수 진행 에러 "+str(e)
        send_error(msg, uno)


def first_trade(key1, key2, coinn, initAsset, intergap, profit, uno):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    #cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 모두 취소
    #canclebidorder(key1, key2, coinn, uno)  # 기존 매수 주문 모두 취소
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset #매수 금액
        buyrest = buymarketpr(key1, key2, coinn, bidasset,uno)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
        time.sleep(1)
    except Exception as e:
        msg = '시장가 구매 에러 '+ str(e)
        send_error(msg, uno)
        print(msg)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        setprice = float(traded["avg_buy_price"]) * (1.0 + (profit / 100.0))
        setprice = calprice(setprice, uno)
        setvolume = traded['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume, uno)
        print("1단계 매도 실행 완료")
    # 추가 예약 매수 실행
        bidprice = ((preprice * 100) - (preprice * intergap)) / 100
        bidprice = calprice(bidprice, uno)
        bidasset = bidasset * 2
        preprice = bidprice  #현재가에 적용
        bidvol = bidasset / bidprice
        buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        print("1단계 매수 실행 완료")
    return None


def mainService(svrno):
    global uno
    users =  dbconn.getsetonsvr(svrno)
    try:
        for user in users:
            setups = dbconn.getmsetup(user)
            for setup in setups: #(471, 18, 20000.0, 9, 1.0, 0.5, 'KRW-ZETA', 'Y', '43', 21, 'N', 6, 'N', datetime.datetime(2024, 10, 21, 9, 35, 4), '100001000010000')
                if setup[7]!="Y":
                    continue #구동중이지 않은 경우 통과
                uno = setup[1]
                holdcnt = setup[11]
                vcoin = setup[6][4:] #코인명
                keys = dbconn.getupbitkey(uno) # 키를 받아 오기
                upbit = pyupbit.Upbit(keys[0], keys[1])
                mycoins = upbit.get_balances()
                mywon = 0 #보유 원화
                myvcoin = 0 #보유 코인
                vcoinprice = 0 #코인 평균 구매가
                myrestvcoin = 0 #잔여 코인
                bidprice = 0
                amt = 0
                amtb = 0
                cnt = 0
                cntb = 0
                calamt = 0
                ordtype = 0 #주문 종류
                for coin in mycoins:
                    if coin["currency"] == "KRW":
                        mywon = float(coin["balance"]) - float(coin["locked"])
                        print("KRW", mywon)
                    if coin["currency"] == vcoin:
                        myvcoin = float(coin["balance"]) + float(coin["locked"])
                        myrestvcoin = float(coin["balance"])
                        vcoinprice = float(coin["avg_buy_price"])
                        print(vcoin,":",myvcoin, "Price :", vcoinprice)
                # 지갑내용 받아오기 - 해당 코인만
                coinn = "KRW-"+vcoin
                curprice = pyupbit.get_current_price(coinn)
                print("코인 현재 시장가", curprice)
                myorders = upbit.get_order(coinn, state='wait')
                cntask = 0 #매도 주문수
                cntbid = 0 #매수 주문수
                lastbidsec = 0
                if myorders is not None:
                    for order in myorders:
                        nowt = datetime.now()
                        if order["side"] == "ask":
                            cntask = cntask + 1
                            last = order["created_at"]
                            last = last.replace("T", " ")
                            last = last[:-6]
                            last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                            lastbidsec = (nowt - last).seconds
                        elif order["side"] == "bid":
                            cntbid = cntbid + 1
                else:
                    cntask = 0
                    cntbid = 0
                norasset = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
                cntpost = 0 #매수 회차 산출 프로세스
                if globals()['stepcnt_{}'.format(setup[0])] == 0:
                    globals()['askcnt_{}'.format(setup[0])] = cntask
                    globals()['bidcnt_{}'.format(setup[0])] = cntbid
                print("이전 매도주문수 ", globals()['askcnt_{}'.format(setup[0])])
                print("현재 매도주문수 ", cntask)
                print("이전 매도주문수 ", globals()['bidcnt_{}'.format(setup[0])])
                print("현재 매수주문수 ", cntbid)
                for order in myorders:
                    if order['side'] == 'ask':
                        amt = float(order['volume']) * float(order['price'])
                        print("기존 매도 금액 ", amt)
                        addamt = float(amt) + float(setup[2]) #회차 계산용 금액 투입금액 플러스
                        cnt = round(addamt / float(setup[2])) #회차 계산
                        print("매도량 산출 배수 ", cnt)
                        calamt = cnt * int(setup[2])
                        if cnt not in norasset:  # 목록에 없을 경우
                            for i in norasset:
                                if cnt >= i:
                                    cntpost += 1
                        else:
                            cntpost = norasset.index(cnt)
                    elif order['side'] == 'bid':
                        amtb = float(order['volume']) * float(order['price'])
                        print("기존 매수 주문 금액 ", amtb)
                        addamtb = float(amtb) + float(setup[2])
                        cntb = round(addamtb / float(setup[2]))
                        print("매수량 산출 배수 ", cntb)
                    else:
                        amtb =float(setup[2])
                        print("기존 매도매수 없음")
                if amtb == 0:
                    amtb = float(setup[2]/2)
                print("현재 산출 회차 단계", cntpost)
                print("이전 산출 회차 단계", globals()['stepcnt_{}'.format(setup[0])])
                print("직전 주문 경과시간 ",lastbidsec,"초")
                holdstat = ""
                if holdcnt <= cntpost:
                    holdstat = "Y"
                else:
                    holdstat = "N"
                # 주문 확인
                if cntask == 0 and cntbid == 0:  #신규주문
                    ordtype = 1
                    cnt = 1
                elif cntask ==0 and cntbid !=0:  #매도후 매수취소
                    ordtype = 2
                elif cntask !=0 and cntbid ==0:  #추가 매수 진행
                    #홀드 및 신호등 체크 !!!!!
                    if lastbidsec <= 10:
                        ordtype = 0
                        print("급격하락 10초 딜레이")
                    else:
                        ordtype = 3
                    if holdstat == "Y":
                        if lastbidsec <= 300:
                            ordtype = 0
                            print("홀드 설정에 의한 5분 딜레이")
                        else:
                            ordtype = 3
                else:
                    ordtype = 0 # 기타
                bidprice = round(amtb * 2)
                print("다음 매수 금액 : ",bidprice)
                #다음 투자금 확인
                trsets = setdetail(setup[8]) #상세 투자 설정
                intvset = trsets[4:13] #투자설정 간격
                marginset = trsets[14:23] #투자설정 이율
                bidintv = intvset[cntpost]
                bidmargin = marginset[cntpost]
                if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS", "KRW-GRT", "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI", "KRW-STG", "KRW-TRX"]:
                    bideaprice = calprice2(float(curprice * (1 - bidintv / 100)),uno) #목표 단가
                else:
                    bideaprice = calprice(float(curprice * (1 - bidintv / 100)), uno)  # 목표 단가
                bidvolume = float(bidprice)/float(bideaprice)
                print("매수설정단가 ", bideaprice)
                print("매수설정개수 ", bidvolume)
                print("설정회차", cntpost)
                print("설정금액",bidprice)
                print("설정간격", bidintv)
                print("설정이윤", bidmargin)
                if myrestvcoin != 0:
                    print("잔여 코인 존재: ", myrestvcoin)
                    order_mod_ask5(keys[0], keys[1], coinn, bidmargin, uno)
                    globals()['askcnt_{}'.format(setup[0])] = 1
                    print("사용자 ", setup[1], "설정번호 ", setup[0], " 코인 ", setup[6], " 매도 재주문")
                    print("------------------------")
                    continue
                if ordtype == 1:
                    print("주문실행 설정", ordtype)
                    first_trade(keys[0], keys[1], coinn, bidprice, bidintv, bidmargin, uno)
                    globals()['askcnt_{}'.format(setup[0])] = 1
                    globals()['bidcnt_{}'.format(setup[0])] = 1
                    globals()['stepcnt_{}'.format(setup[0])] = 2  # 거래단계 수
                elif ordtype == 2:
                    print("주문실행 설정", ordtype)
                    canclebidorder(keys[0], keys[1], coinn, uno)
                    globals()['stepcnt_{}'.format(setup[0])] = 1
                elif ordtype == 3:
                    print("주문실행 설정", ordtype)
                    #보유 현금이 충분할 경우만 실행
                    if mywon >= bidprice:
                        add_new_bid(keys[0],keys[1],coinn,bideaprice,bidvolume,uno)
                        globals()['stepcnt_{}'.format(setup[0])] = globals()['stepcnt_{}'.format(setup[0])] + 1 # 거래단계 수
                        globals()['bidcnt_{}'.format(setup[0])] = 1
                    else:
                        print("현금 부족으로 주문 패스 (보유현금 :",mywon,")")
                else:
                    print("이번 회차 주문 설정 없음")
                # 주문 기록
                print("사용자 ",setup[1],"설정번호 ",setup[0]," 코인 ",setup[6], " 종료")
                print("------------------------")
    except Exception as e:
        msg = "메인 루프 에러 :" + str(e)
        send_error(msg, uno)
        print("메인 루프 에러 :", e)
    finally:
        ntime = datetime.now()
        print('$$$$$$$$$$$$$$$$$$$')
        print('거래점검 시간', ntime)
        print('점검 서버', svrno)
        print('$$$$$$$$$$$$$$$$$$$')
        dbconn.clearcache()  # 캐쉬 삭제



def service_restart():
    tstamp = datetime.now()
    print("Service Restart : ", tstamp)
    myip = requests.get('http://ip.jsontest.com').json()['ip']
    msg = "Server " + str(svrno) + " Service Restart : " + str(tstamp) + "  at  " + str(myip) + " Service Ver : "+ str(mainver)
    send_error(msg, '0')
    os.execl(sys.executable, sys.executable, *sys.argv)


def service_start():
    tstamp = datetime.now()
    print("Service Start : ", tstamp)
    myip = requests.get('http://ip.jsontest.com').json()['ip']
    msg = "Server " + str(svrno) + " Service Start : " + str(tstamp) + "  at  " + str(myip) + " Service Ver : "+ str(mainver)
    dbconn.servicelog(msg,0)


def send_error(err, uno):
    dbconn.errlog(err, uno)


def get_lastbuy(key1, key2, coinn, uno):
    global lastbuy
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn, state='wait')
        lastbuy = dbconn.getlog(uno,'BID', coinn)
        if lastbuy is None :
            lastbuy = datetime.now()
        for order in orders: # 내용이 있을 경우 업데이트
            if order["side"] == 'bid':
                last = order["created_at"]
                last = last.replace("T", " ")
                last = last[:-6]
                last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if last != lastbuy:
                    dbconn.tradelog(uno,"BID",coinn, last)
                    lastbuy = dbconn.getlog(uno,'BID', coinn)
    except Exception as e:
        msg = "최근 거래 조회 에러 : " + str(e)
        send_error(msg,uno)
    finally:
        return lastbuy


def get_lasttrade(key1, key2, coinn, uno):
    global lasthold
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn, state='done',limit=1)
        lasthold = dbconn.getlog(uno,'HOLD', coinn)
        if lasthold is None :
            lasthold = datetime.now()
        for order in orders:
            if order["side"] == 'bid':
                last = order["created_at"]
                last = last.replace("T", " ")
                last = last[:-6]
                last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if last != lasthold:
                    dbconn.tradelog(uno,"HOLD",coinn, last)
    except Exception as e:
        msg = "최종 거래 점검 에러 : " + str(e)
        send_error(msg,uno)
    finally:
        lasthold = dbconn.getlog(uno, 'HOLD', coinn)[0]
        return lasthold


def chk_lastbid(coinn, uno, restmin):
    now = datetime.now()
    lastbid = dbconn.getlog(uno,'BID', coinn)[0]
    lastbid = str(lastbid)
    if lastbid != None:
        past = datetime.strptime(lastbid, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        print("구매 경과 시간 :", diffmin, "분")
        if diffmin <= restmin:
            return "DELAY"
        else:
            return "SALE"
    else:
        print("직전 구매 이력 없음")


def save_holdtime(uno,coinn):
    dbconn.tradelog(uno,'HOLD',coinn)


def check_hold(min,uno,coinn):
    now = datetime.now()
    last = dbconn.getlog(uno,'HOLD',coinn)[0]
    last = str(last)
    if last != None:
        past = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        print("경과시간 : ", diffmin,"분")
        if diffmin <= min:
            return "HOLD"
        else:
            return "SALE"
    else:
        dbconn.tradelog(uno,'HOLD',coinn)  #구매 카운트 시작


def check_holdstart(min,uno,coinn): # 홀드시작이후 시간 체크
    now = datetime.now()
    last = dbconn.getlog(uno,'HOLD', coinn)[0]
    last = str(last)
    if last != None:
        past = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        if diffmin <= min:
            return "HOLD"
        else:
            return "SALE"
    else:
        save_holdtime(uno, coinn)  #새로운 홀드 카운트 시작


cnt = 1
setons = dbconn.getseton()
users = dbconn.getsetonsvr(svrno)
for user in users:
    setups = dbconn.getmsetup(user)
    for setup in setups:
        globals()['askcnt_{}'.format(setup[0])] = 0  # 매도거래 수
        globals()['bidcnt_{}'.format(setup[0])] = 0  # 매수거래 수
        globals()['stepcnt_{}'.format(setup[0])] = 0  # 거래단계 수
service_start() # 시작시간 기록
while True:
    print("구동 횟수 : ", cnt)
    for seton in setons:
        try:
            mainService(svrno)
            cnt = cnt + 1
        except Exception as e:
            myset = loadmyset(seton)
            uno = myset[1]
            msg = "메인 while 반복문 에러 : "+str(e)
            send_error(msg, uno)
        finally:
            if cnt > 1800:  # 0.5시간 마다 재시작
                cnt = 1
                service_restart()
        time.sleep(1)

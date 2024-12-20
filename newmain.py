import time
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
mainver = 241023001


def loadmyset(uno):
    global mysett
    try:
        mysett = dbconn.getsetups(uno)
    except Exception as e:
        msg = "나의 세팅 조회 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return mysett


def getkeys(uno):
    global mykey
    try:
        mykey = dbconn.getupbitkey(uno)
    except Exception as e:
        msg = "API 키조회 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return mykey


def getorders(key1, key2, coinn, uno):
    global orders
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn)
    except Exception as e:
        msg = "주문 내역 조회 에러 " + str(e)
        send_error(msg, uno)
    finally:
        return orders


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


def sellmarketpr(key1, key2, coinn, setvol, uno):
    global orders
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.sell_market_order(coinn, setvol)
    except Exception as e:
        msg = " 시장가 매도 에러 " + str(e)
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
                    print("잔고 남아 재거래 실행")
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


def checkbidorder(key1, key2, coinn, uno):
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn)
        for order in orders:
            if order['side'] == 'bid':
                return True
            else:
                return False
    except Exception as e:
        msg = "매수 주문 체크 에러 " + str(e)
        send_error(msg, uno)


def loadtrset(sno, uno):
    global trset
    try:
        trset = dbconn.setdetail(sno)
        trsetting = trset[3:23]
        return trsetting
    except Exception as e:
        msg = "거래 세팅 조회 에러 " + str(e)
        send_error(msg, uno)

def order_mod_ask(key1, key2, coinn, profit, uno):  #이윤 고정식 계산 방식
    print("매도 주문 재생성")
    try:
        preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
        cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.005 + (profit / 100.0))
        setprice = calprice(setprice, uno)
        setvolume = tradednew['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = "매도주문 갱신 에러 "+ str(e)
        send_error(msg, uno)


def order_mod_ask2(key1, key2, coinn, profit, uno):  #이윤 변동식 계산 방식
    print("매도 주문 재생성2")
    try:
        cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(
            tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit[0] / 100)
        print("재설정 이윤 :", profit[0])
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        setprice = calprice(setprice, uno)
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, totalvol, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = '매도주문2 갱신 에러 '+str(e)
        send_error(msg, uno)


def order_mod_ask3(key1, key2, coinn, profit, uno):  #분산형 매도주문 생성
    print("매도 주문 재생성 3")
    try:
        cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(
            tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit[0] / 100)
        print("재설정 이윤 :", profit[0])
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        setprice = calprice(setprice, uno)
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, totalvol, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = '매도주문 갱신3 에러 '+str(e)
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
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, totalvol, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = '매도주문5 갱신 에러 '+str(e)
        send_error(msg, uno)


def clear_param():
    setons = dbconn.getseton()
    for seton in setons:
        globals()['lcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
        globals()['bcnt_{}'.format(seton[0])] = 0  # 점검횟수 초기화
        globals()['tcnt_{}'.format(seton[0])] = 0  # 거래 예약 횟수 초기화
        globals()['askcnt_{}'.format(seton[0])] = 0  # 매도거래 수
        globals()['bidcnt_{}'.format(seton[0])] = 0  # 매수거래 수
        globals()['mysell_{}'.format(seton[0])] = 0  # 매도 설정 금액
    return None


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


def order_new_bid_mod(key1, key2, coinn, initAsset, intval, intergap, profit, uno):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 모두 취소
    canclebidorder(key1, key2, coinn, uno)  # 기존 매수 주문 모두 취소
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset
        buyrest = buymarketpr(key1, key2, coinn, bidasset,uno)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
    except Exception as e:
        myset = loadmyset(seton)
        uno = myset[1]
        msg = '시장가 구매 에러 '+ str(e)
        send_error(msg, uno)
        print(e)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.0 + (profit / 100.0))
        setprice = calprice(setprice, uno)
        setvolume = traded['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume, uno)
    # 추가 예약 매수 실행
    for i in range(1, intval + 1):
        bidprice = ((preprice * 100) - (preprice * intergap[i])) / 100
        bidprice = calprice(bidprice, uno)
        bidasset = bidasset * 2
        preprice = bidprice  #현재가에 적용
        bidvol = bidasset / bidprice
        buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        print("매수 실행")
    globals()['mybuy_{}'.format(seton[0])] = 1  # 매도 설정 횟수
    return None


def add_new_bid(key1, key2, coinn, bidprice, bidvol, uno):
    try:
        ret = buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        # tradelog(uno,"BID", coinn, datetime.now()) #주문 기록
        return ret
    except Exception as e:
        msg = "추가매수 진행 에러 "+str(e)
        send_error(msg, uno)


def first_trade(key1, key2, coinn, initAsset, intergap, profit, uno):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 모두 취소
    canclebidorder(key1, key2, coinn, uno)  # 기존 매수 주문 모두 취소
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset #매수 금액
        buyrest = buymarketpr(key1, key2, coinn, bidasset,uno)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
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
                vcoin = setup[6][4:] #코인명
                keys = dbconn.getupbitkey(uno) # 키를 받아 오기
                upbit = pyupbit.Upbit(keys[0], keys[1])
                mycoins = upbit.get_balances()
                mywon = 0 #보유 원화
                myvcoin = 0 #보유 코인
                vcoinprice = 0 #코인 평균 구매가
                myrestvcoin = 0
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
                myorders = upbit.get_order(coinn)
                cntask = 0 #매도 주문수
                cntbid = 0 #매수 주문수
                for order in myorders:
                    if order["side"] == "ask":
                        cntask = cntask + 1
                    if order["side"] == "bid":
                        cntbid = cntbid + 1
                norasset = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023]
                cntpost = 0 #매수 회차 산출 프로세스
                for order in myorders:
                    if order['side'] == 'ask':
                        amt = float(order['volume']) * float(order['price'])
                        print("기존 투입 금액 ", amt)
                        cnt = round(amt / float(setup[2]))
                        print("산출 배수 ", cnt)
                        if cnt not in norasset:  # 목록에 없을 경우
                            for i in norasset:
                                if cnt > i:
                                    cntpost += 1
                        else:
                            cntpost = norasset.index(cnt) + 1
                print("산출 회차 ", cntpost)
                # 주문 확인
                bidprice = 0
                bidprice = float(setup[2])*2**(cntpost)
                print("다음 매수 금액 : ",bidprice)
                #다음 투자금 확인
                ordtype = 0
                if cntask == 0 and cntbid == 0:
                    print("새로운 주문")
                    ordtype = 1
                elif cntask ==0 and cntbid !=0:
                    print("취소후 재주문")
                    ordtype = 2
                elif cntask !=0 and cntbid ==0:
                    print("추가 매수 주문")
                    ordtype = 3
                else:
                    print("매도매수 대기중")
                    ordtype = 0
                # 주문 종류 - 신규, 추가, 재매도 결정
                trsets = setdetail(setup[8]) #상세 투자 설정
                intvset = trsets[3:13] #투자설정 간격
                marginset = trsets[13:23] #투자설정 이율
                bidintv = intvset[cntpost]
                bidmargin = marginset[cntpost]
                bideaprice = calprice(float(curprice*(1+bidintv/100)),uno) #목표 단가
                bidvolume = float(bidprice)/float(bideaprice)
                print("매수설정단가 ", bideaprice)
                print("매수설정개수 ", bidvolume)
                print("설정회차", cntpost)
                print("설정금액",bidprice)
                print("설정간격", bidintv)
                print("설정이윤", bidmargin)
                if ordtype == 1:
                    print("주문실행 설정", ordtype)
                    first_trade(keys[0], keys[1], coinn,bidprice, bidintv, bidmargin,uno)
                if ordtype == 2:
                    print("주문실행 설정", ordtype)
                    canclebidorder(keys[0], keys[1], coinn, uno)

                if ordtype == 3:
                    print("주문실행 설정", ordtype)
                    #보유 현금이 충분할 경우만 실행
                    if mywon >= bidprice:
                        add_new_bid(keys[0],keys[1],coinn,bideaprice,bidvolume,uno)
                    else:

                        print("현금 부족으로 주문 패스 (보유현금 :",mywon,")")
                # 주문 실행
                if myrestvcoin != 0:
                    print("잔여 코인 존재: ", myrestvcoin)
                    order_mod_ask5(keys[0], keys[1], coinn, bidmargin, uno)
                # 주문 수정
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


def cntbid(ckey1, ckey2, coinn, iniAsset, dblyn, uno):
    global cntpost
    try:
        cntpost = 1
        orders = getorders(ckey1, ckey2, coinn, uno)
        norasset = [1,3,7,15,31,63,127,255,511,1023]
        dblasset = [1,3,9,27,81,243,729,2187,6561,19683]
        for order in orders:
            if order['side'] == 'ask':
                amt = float(order['volume']) * float(order['price'])
                print("기존 투입 금액 ",amt)
                cnt = round(amt/float(iniAsset))
                print("산출 배수 ",cnt)
                if dblyn != 'Y':
                    if cnt not in norasset: # 목록에 없을 경우
                        for i in norasset:
                            if cnt > i:
                                cntpost += 1
                    else:
                        cntpost = norasset.index(cnt) + 1
                else:
                    if cnt not in dblasset:
                        for i in dblasset:
                            if cnt > i:
                                cntpost += 1
                    else:
                        cntpost = dblasset.index(cnt) + 1
                print("산출 회차 ", cntpost)
    except Exception as e:
        msg = "매수단계 카운트 에러" + str(e)
        send_error(msg, uno)
    finally:
        return cntpost


cnt = 1
setons = dbconn.getseton()
for seton in setons:
    globals()['lcnt_{}'.format(seton[0])] = 0 # 거래단계 초기화
    globals()['bcnt_{}'.format(seton[0])] = 0  # 점검횟수 초기화
    globals()['tcnt_{}'.format(seton[0])] = 0  # 거래 예약 횟수 초기화
    globals()['askcnt_{}'.format(seton[0])] = 0  # 매도거래 수
    globals()['bidcnt_{}'.format(seton[0])] = 0  # 매수거래 수
    globals()['mysell_{}'.format(seton[0])] = 0  # 매도 설정 금액
    globals()['mybuy_{}'.format(seton[0])] = 0  # 매수 단계 카운트
service_start() # 시작시간 기록
while True:
    print("구동 횟수 : ", cnt)
    for seton in setons:
        try:
            #trace_trade_method(svrno)
            mainService(svrno)
            cnt = cnt + 1
        except Exception as e:
            myset = loadmyset(seton)
            uno = myset[1]
            msg = "메인 while 반복문 에러 : "+str(e)
            send_error(msg, uno)
        finally:
            if cnt > 3600:  # 1시간 마다 재시작
                cnt = 1
                service_restart()
        time.sleep(3)

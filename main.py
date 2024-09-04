import time
from datetime import datetime
import dbconn
import pyupbit
import dotenv
import os
import sys
import requests


dotenv.load_dotenv()
bidcnt = 1
svrno = os.getenv("server_no")
mainver = 240904001


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
                    print("잔고 남아 재거래")
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
        return ret
    except Exception as e:
        msg = "추가매수 진행 에러 "+str(e)
        send_error(msg, uno)


def trace_trade_method(svrno):
    global orderstat, key1, key2, coinn, askcnt, bidcnt, traded, seton, targetamt, pbidcnt
    setons = dbconn.getsetonsvr(svrno)  # 서버별 사용자 로드
    try:
        for seton in setons:  # 개별 프로세스 시작
            keys = getkeys(seton)
            key1 = keys[0]  # 키로드
            key2 = keys[1]  # 키로드
            myset = loadmyset(seton)  # 트레이딩 셋업로드
            print("투자설정 내용 : ", myset)
            print("User ", myset[1], "Coin ", myset[6], " seed ", myset[2], " start")
            bidcount = cntbid(key1, key2, myset[6], myset[2], myset[12], myset[1])  # 매수 단계 확인
            if myset[7] == 'Y':  # 주문 ON 인 경우
                iniAsset = myset[2]  # 기초 투입금액
                interVal = myset[3]  # 매수 횟수
                trset = myset[8]  # 투자 설정
                holdpost = myset[11] # 홀드 포지션
                if holdpost > 2:
                    if bidcount >= holdpost:
                        # dbconn.setholdYN(myset[0] ,'Y')  # 홀드 설정
                        print("홀드 조건 해당")
                    else:
                        print("홀드 조건 아님")
                        pass  #  dbconn.setholdYN(myset[0] ,'N')
                else:
                    print("홀드 설정 아님")
                print("매수 카운트 11 : ", bidcount)
                print("홀드 포지션 11 : ", holdpost)
                trsetting = loadtrset(trset, myset[1])  # 투자 설정 로드
                intergap = trsetting[:10]  # 매수 간격
                # print("매수간격 설정내용 :", intergap)
                intRate = trsetting[10:20]  # 매수 이율
                # print("매수 이율 설정 내용 : ", intRate)
                coinn = myset[6]  # 매수 종목
                cointrend = get_trend(coinn,myset[1])  # 코인 트렌드 검색
                coinsignal = dbconn.getSignal(coinn) # 시간당 코인 트렌드 조회
                print("트렌드 시그날 내용 : ",coinsignal)
                orderstat = getorders(keys[0], keys[1], myset[6], myset[1])  # 주문현황 조회
                globals()['askcnt_{}'.format(seton[0])] = 0
                globals()['bidcnt_{}'.format(seton[0])] = 0
                for order in orderstat:  # 주문 확인
                    if order["side"] == 'ask':
                        globals()['askcnt_{}'.format(seton[0])] = globals()['askcnt_{}'.format(seton[0])] + 1
                    elif order["side"] == 'bid':
                        globals()['bidcnt_{}'.format(seton[0])] = globals()['bidcnt_{}'.format(seton[0])] + 1
                print("매도요청 수 : ", globals()['askcnt_{}'.format(seton[0])])  # 매도요청 수
                print("매수요청 수 : ", globals()['bidcnt_{}'.format(seton[0])])  # 매수요청 수
                traded = checktraded(keys[0], keys[1], coinn, myset[1])  # 설정 코인 지갑내 존재 확인
                print(traded)
                if myset[10] == 'Y': # 홀드 주문 취소 프로세스
                    print("홀드 설정 사용중")
                    if bidcount >= holdpost:
                        # dbconn.setholdYN(myset[0] ,'Y')  # 홀드 설정
                        dlytime = check_hold(60,myset[1],coinn)
                        if dlytime != "SALE":
                            canclebidorder(key1, key2, coinn, myset[1])  # 전체 매수 주문 취소
                            print("홀드 조건에 1시간 이내 매수주문 취소")
                        print("홀드 조건 해당")
                    else:
                        print("홀드 조건 아님")
                        pass  #  dbconn.setholdYN(myset[0] ,'N')
                else:
                    print("홀드 설정 미사용")
                if traded == None: # 최초 거래 실시
                    order_new_bid_mod(key1, key2, coinn, iniAsset, 1, intergap, intRate[1], myset[1]) # 구간은 리스트로 이율은 상수로
                elif float(traded["balance"]) + float(traded["locked"]) > 0:
                    if float(traded["balance"]) > 0:
                        print("매도 수정 처리 1")
                        inrate = intRate[bidcount+1]
                        print(bidcount," 단계 이율 적용 : ", inrate)
                        order_mod_ask5(key1, key2, coinn, inrate, myset[1])  # 매도 수정 처리
                    elif globals()['bidcnt_{}'.format(seton[0])] == 0:  # 매수주문 없음
                        print("매수 주문 없음 check 추가 매수 프로세스")
                        if cointrend[1] > -3:
                            print("신호등 긍정 ", cointrend[1])
                            apprate = float(intergap[bidcount])/100 # 매수단계별 구간 적용
                            print("매수 단계 :",bidcount,"적용 비율 ",apprate)
                            if bidcount >= holdpost:  # 홀드 구간
                                bidprice = float(pyupbit.get_current_price(coinn)) * (1-float(apprate)*1.2) # 현재가에 단계 구간 적용(120% 구간 적용)
                            else:
                                bidprice = float(pyupbit.get_current_price(coinn)) * (1-float(apprate))  # 현재가에 단계 구간 적용
                            bidprice = calprice(bidprice, myset[1]) # 적용 가격 변환
                            print("적용 가격: ", bidprice)
                            totalamt = (float(traded["balance"]) + float(traded["locked"])) * float(traded["avg_buy_price"])
                            if myset[12] == "Y":
                                pbidcnt = bidcount
                                targetamt = round(totalamt * 2) # 구매가의 2배 구매
                                print(targetamt)
                            else:
                                pbidcnt = bidcount
                                targetamt = iniAsset*2**pbidcnt
                            print("구매단계 체크 : ", pbidcnt)
                            print("주문 금액 체크 : ", targetamt)
                            bidvol = targetamt / bidprice #구매 수량 산출
                            print("주문 수량 산출 : ",bidvol)
                            prevbid = get_lastbuy(key1, key2, coinn, myset[1])
                            print("직전 구매 시간",prevbid)
                            # 일반 구매 시 딜레이 타임
                            if bidcount >= holdpost:
                                dlytime = check_hold(60,myset[1],coinn) #홀드 구매 딜레이 신호등
                            else:
                                dlytime = check_hold(10, myset[1], coinn) # 기본 구매 딜레이 신호
                            if dlytime == "SALE":
                                print("딜레이신호등 통과")
                                if bidcount >= holdpost:  #홀드 구간 비율 상승 재주문
                                    print("홀드 구간 매수재주문")
                                    add_new_bid(key1, key2, coinn, bidprice, bidvol, myset[1])
                                else:
                                    print("일반 구간 매수재주문")
                                    add_new_bid(key1, key2, coinn, bidprice, bidvol, myset[1])
                            else:
                                print("딜레이신호등 작동중")
                                if pbidcnt in[1,2,3,4]:
                                    print("초기 구매 딜레이 없이 작동")
                                    add_new_bid(key1, key2, coinn, bidprice, bidvol, myset[1])
                                pass
                        else:
                            print("신호등 부정", cointrend[1])
                            pass  # 대기
                        print(get_lasttrade(key1, key2, coinn, myset[1]))
                    else:
                        print("매도 대기중")
                        pass
            else:
                print("User ", myset[1], 'Status is Off')
            #get_lastbuy(key1, key2, coinn, myset[1])
            print("User ", myset[1], " ", myset[6], " finish")
    except Exception as e:
        myset = loadmyset(seton)
        uno = myset[1]
        msg = "메인 루프 에러 :"+str(e)
        send_error(msg, uno)
        print("메인 루프 에러 :", e)
    finally:
        ntime = datetime.now()
        print('**********')
        print('거래점검 시간', ntime)
        print('거래점검 완료', cnt)
        print('**********')
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
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn, state='wait')
    lastbuy = dbconn.getlog(uno,'BID', coinn)[0]
    if lastbuy ==None :
        lastbuy = datetime.now()
    for order in orders: # 내용이 있을 경우 업데이트
        if order["side"] == 'bid':
            last = order["created_at"]
            last = last.replace("T", " ")
            last = last[:-6]
            last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            if last != lastbuy:
                dbconn.tradelog(uno,"BID",coinn, last)
            else:
                pass
    lastbid = dbconn.getlog(uno,'BID', coinn)[0]
    return lastbid


def get_lasttrade(key1, key2, coinn, uno):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn, state='done',limit=1)
    lasthold = dbconn.getlog(uno,'HOLD', coinn)[0]
    for order in orders:
        if order["side"] == 'bid':
            last = order["created_at"]
            last = last.replace("T", " ")
            last = last[:-6]
            last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            if last != lasthold:
                dbconn.tradelog(uno,"HOLD",coinn, last)
            else:
                pass
    lasthold = dbconn.getlog(uno,'HOLD', coinn)[0]
    return lasthold


def chk_lastbid(coinn, uno, restmin):
    now = datetime.now()
    lastbid = dbconn.getlog(uno,'BID', coinn)
    lastbid = str(lastbid[0])
    if lastbid != None:
        past = datetime.strptime(lastbid, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        print("구매 경과 시간 :", diffmin, "분")
        if diffmin <= restmin:
            return "DELAY"
        else:
            return "BID"
    else:
        print("직전 구매 이력 없음")


def save_holdtime(uno,coinn):
    dbconn.tradelog(uno,'HOLD',coinn)


def check_hold(min,uno,coinn):
    now = datetime.now()
    last = dbconn.getlog(uno,'HOLD',coinn)
    last = str(last[0])
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
    last = dbconn.getlog(uno,'HOLD', coinn)
    last = str(last[0])
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
            trace_trade_method(svrno)
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
        time.sleep(1)

import time
from datetime import datetime
import dbconn
import pyupbit
import dotenv
import os


dotenv.load_dotenv()
bidcnt = 1
svrno = os.getenv("server_no")


def loadmyset(uno):
    mysett = dbconn.getsetups(uno)
    return mysett


def getkeys(uno):
    mykey = dbconn.getupbitkey(uno)
    return mykey


def getorders(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    return orders


def buymarketpr(key1, key2, coinn, camount):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.buy_market_order(coinn, camount)
    return orders


def buylimitpr(key1, key2, coinn, setpr, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.buy_limit_order(coinn, setpr, setvol)
    return orders


def sellmarketpr(key1, key2, coinn, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.sell_market_order(coinn, setvol)
    return orders


def selllimitpr(key1, key2, coinn, setpr, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.sell_limit_order(coinn, setpr, setvol)
    return orders


def checktraded(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    checktrad = upbit.get_balances()
    for wallet in checktrad:
        if "KRW-" + wallet['currency'] == coinn:
            if float(wallet['balance']) != 0.0:
                print("잔고 남아 재거래")
            else:
                print('매도 거래 대기중')
            return wallet
        else:
            pass
    if checktrad is None:
        pass


def calprice(bidprice):
    if bidprice >= 2000000:
        bidprice = round(bidprice, -3)
    elif bidprice >= 1000000 and bidprice < 20000000:
        bidprice = round(bidprice, -3) + 500
    elif bidprice >= 500000 and bidprice < 1000000:
        bidprice = round(bidprice, -2)
    elif bidprice >= 100000 and bidprice < 500000:
        bidprice = round(bidprice, -2) + 50
    elif bidprice >= 10000 and bidprice < 100000:
        bidprice = round(bidprice, -1)
    elif bidprice >= 1000 and bidprice < 10000:
        bidprice = round(bidprice)
    elif bidprice >= 100 and bidprice < 1000:
        bidprice = round(bidprice, 1)
    elif bidprice >= 10 and bidprice < 100:
        bidprice = round(bidprice, 2)
    elif bidprice >= 1 and bidprice < 10:
        bidprice = round(bidprice, 3)
    else:
        bidprice = round(bidprice, 4)
    return bidprice


def cancelaskorder(key1, key2, coinn): #매도 주문 취소
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    for order in orders:
        print(order)
        if order['side'] == 'ask':
            upbit.cancel_order(order['uuid'])
            print("Canceled")


def canclebidorder(key1, key2, coinn):  #코인 청산
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    try:
        if orders is not None:
            for order in orders:
                upbit.cancel_order(order["uuid"])
        else:
            pass
    except Exception as e:
        print('cancel bid error',e)


def checkbidorder(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    for order in orders:
        if order['side'] == 'bid':
            return True
        else:
            return False


def loadtrset(sno):
    trset = dbconn.setdetail(sno)
    trsetting = trset[3:23]
    return trsetting


def order_cnt_trade(svrno):
    global orderstat, key1, key2, coinn, askcnt, bidcnt, traded
    setons = dbconn.getsetonsvr(svrno)  #서버별 사용자 로드
    try:
        for seton in setons:
            keys = getkeys(seton)
            key1 = keys[0]  # 키로드
            key2 = keys[1]  # 키로드
            myset = loadmyset(seton)  # 트레이딩 셋업로드
            print("User ", myset[1], " start")
            iniAsset = myset[2]  # 기초 투입금액
            interVal = myset[3]  # 매수 횟수
            trset = myset[8]
            trsetting = loadtrset(trset)
            intergap = trsetting[:10]  # 매수 간격
            intRate = trsetting[10:20]  # 매수 이율
            coinn = myset[6]  # 매수 종목
            if myset[7] == 'Y':  # 주문 ON 인 경우
                print('주문 개시 user', seton[0])
                preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
                orderstat = getorders(keys[0], keys[1], myset[6])  # 주문현황 조회
                if globals()['tcnt_{}'.format(seton[0])] == 0:  #거래단계 처음
                    traded = checktraded(keys[0], keys[1], coinn)  # 설정 코인 지갑내 존재 확인
                    if traded is None:
                        print('최초 거래 시작')
                        order_new_bid(keys[0], keys[1], coinn, iniAsset, interVal, intergap, intRate)
                    else:
                        print('지갑에 코인 존재')
                        bidcnt = 0
                        askcnt = 0
                        orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                        if orderstat is None: #주문 없을때
                            print('지갑에 코인을 정리해 주세요')
                            break
                        else:
                            for order in orderstat:
                                if order['side'] == 'bid':
                                    bidcnt += 1
                                elif order['side'] == 'ask':
                                    askcnt += 1
                            globals()['askcnt_{}'.format(seton[0])] = askcnt  # 매수거래 수 확인
                            globals()['bidcnt_{}'.format(seton[0])] = bidcnt  # 매도거래 수 확인
                            globals()['tcnt_{}'.format(seton[0])] = 2  # 확인 단계로 진행
                            print('ask 수', globals()['askcnt_{}'.format(seton[0])])
                            print('bid 수', globals()['bidcnt_{}'.format(seton[0])])
                            if traded['balance'] != 0.0:
                                order_mod_ask2(keys[0], keys[1], coinn, intRate) #주문이 있는데 잔고가 있을경우 매도 재설정
                elif globals()['tcnt_{}'.format(seton[0])] == 1:
                    print('1단계 거래') # 주문 카운트
                    bidcnt1 =0
                    askcnt1 =0
                    orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                    print('주문현황', orderstat)
                    for order in orderstat:
                        if order['side'] == 'bid':
                            bidcnt1 += 1
                        elif order['side'] == 'ask':
                            askcnt1 += 1
                        #주문 확인 후 2단계로
                        globals()['askcnt_{}'.format(seton[0])] = askcnt1  # 매수거래 수 확인
                        globals()['bidcnt_{}'.format(seton[0])] = bidcnt1  # 매도거래 수 확인
                        globals()['tcnt_{}'.format(seton[0])] = 2  # 확인 단계로 진행
                elif globals()['tcnt_{}'.format(seton[0])] == 2:
                    print('2단계 거래')
                    bidcnt2 = 0
                    askcnt2 = 0
                    # 매수거래 카운트
                    orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                    for order in orderstat:
                        if order['side'] == 'bid':
                            bidcnt2 += 1
                        elif order['side'] == 'ask':
                            askcnt2 += 1
                    print('bidcnt2', bidcnt2)
                    print('globbidcnt', globals()['bidcnt_{}'.format(seton[0])])
                    print('askcnt2', askcnt2)
                    print('globbidcnt', globals()['askcnt_{}'.format(seton[0])])
                    if bidcnt2 != globals()['bidcnt_{}'.format(seton[0])]:
                        print('bidcnt2', bidcnt2)
                        print('globbidcnt', globals()['bidcnt_{}'.format(seton[0])])
                        #거래수 다를시 재설정
                        print('추가 매수에 의한 재설정')
                        order_mod_ask2(keys[0], keys[1], coinn, intRate)
                        globals()['tcnt_{}'.format(seton[0])] = 1  # 거래단계 초기화
                    elif askcnt2 == 0:  # 전체 거래 취소 후 재구매
                        print('매도 완료에 따른 재 설정', askcnt2)
                        canclebidorder(key1, key2, coinn)
                        globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
                else:
                    print('나머지 단계 거래')
                    #매수 평균가 조회
                    myeve = float(traded["avg_buy_price"])
                    #매도 주문 금액 조회
                    myask = globals()['mysell_{}'.format(seton[0])]
                    # 매수평균* 이율 과 매도 주문 비교
                    if (myask/myeve*100-100 > intRate[0]):
                        order_mod_ask2(keys[0], keys[1], coinn, intRate)
                        print("금액추적 매도주문 재설정")
                    else:
                        print("주문 금액 비율 :", myask/myeve*100)
                    # 차이 발생이 일정비율 이상시 재주문

                chkcoin = checktraded(key1, key2, coinn)  # 지갑 점검
                if chkcoin is None: # 지갑내 해당코인이 없을 경우
                    canclebidorder(key1, key2, coinn) # 주문 취소
                    globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
            else:
                print('-----------------------')
                print('주문 대기 user', seton[0])
                print('-----------------------')
                globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
                chkcoin = checktraded(key1, key2, coinn)  # 지갑 점검
                if chkcoin is None:  # 지갑내 해당코인이 없을 경우
                    canclebidorder(key1, key2, coinn)
                print('-----------------------')
    except Exception as e:
        print('level 1 Error :', e)
    finally:
        ntime = datetime.now()
        print('**********')
        print('거래점검 시간', ntime)
        print('거래점검 완료', cnt)
        print('**********')
        dbconn.clearcache()  # 캐쉬 삭제


def order_new_bid(key1, key2, coinn, initAsset, intval, intergap, profit):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset
        buyrest = buymarketpr(key1, key2, coinn, bidasset)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
        globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
    except Exception as e:
        print(e)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.0 + (profit[0] / 100.0))
        setprice = calprice(setprice)
        setvolume = traded['balance']
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, setvolume)
    # 추가 예약 매수 실행
    for i in range(1, intval + 1):
        bidprice = ((preprice * 100) - (preprice * intergap[i])) / 100
        bidprice = calprice(bidprice)
        bidasset = bidasset * 2
        preprice = bidprice #현재가에 적용
        bidvol = bidasset / bidprice
        print('interval ', i, '예약 거래 적용')
        print('매수가격', bidprice)
        print('매수금액', bidasset)
        print('매수수량', bidvol)
        if globals()['tcnt_{}'.format(seton[0])] == 1:  # 구매 신호에 따라 구매 진행
            buylimitpr(key1, key2, coinn, bidprice, bidvol)
            print("매수 실행")
        else:
            print("매수 PASS")
    # 설정된 추가 매수 진행
    globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 완료 설정
    #주문 개수 확인
    return None


def order_new_bid2(key1, key2, coinn, initAsset, intval, intergap, profit): #고정간격 기법 새구매
    global buyrest, bidasset, bidcnt, askcnt
    print("고정간격 새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset
        buyrest = buymarketpr(key1, key2, coinn, bidasset)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
        globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
    except Exception as e:
        print(e)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.0 + (profit[0] / 100.0))
        setprice = calprice(setprice)
        setvolume = traded['balance']
        globals()['mysell_{}'.format(seton[0])] = setprice
        # 분산 매도주문 입력

        selllimitpr(key1, key2, coinn, setprice, setvolume)
    # 추가 예약 매수 실행 - 균등 방법으로 변경
    for i in range(1, intval + 1):
        bidprice = ((preprice * 100) - (preprice * intergap[i])) / 100
        bidprice = calprice(bidprice)
        bidasset = bidasset * 2
        preprice = bidprice #현재가에 적용
        bidvol = bidasset / bidprice
        print('interval ', i, '예약 거래 적용')
        print('매수가격', bidprice)
        print('매수금액', bidasset)
        print('매수수량', bidvol)
        if globals()['tcnt_{}'.format(seton[0])] == 1:  # 구매 신호에 따라 구매 진행
            buylimitpr(key1, key2, coinn, bidprice, bidvol)
            print("매수 실행")
        else:
            print("매수 PASS")
    # 설정된 추가 매수 진행
    globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 완료 설정
    #주문 개수 확인
    return None


def order_mod_ask(key1, key2, coinn, profit): #이윤 고정식 계산 방식
    print("매도 주문 재생성")
    try:
        preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
        cancelaskorder(key1, key2, coinn)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.005 + (profit / 100.0))
        setprice = calprice(setprice)
        setvolume = tradednew['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume)
        # 새로운 매도 주문
    except Exception as e:
        print('매도주문 갱신 에러 ',e)
    finally:
        print('매도주문 갱신')
        globals()['tcnt_{}'.format(seton[0])] = 3  # 구매 완료 설정
        # 새로운 주문 완료
    return None


def order_mod_ask2(key1, key2, coinn, profit): #이윤 변동식 계산 방식
    print("매도 주문 재생성")
    try:
        cancelaskorder(key1, key2, coinn)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit[0] / 100)
        print("재설정 이윤 :", profit[0])
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        setprice = calprice(setprice)
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, totalvol)
        # 새로운 매도 주문
    except Exception as e:
        print('매도주문 갱신 에러 ',e)
    finally:
        print('매도주문 갱신')
        globals()['tcnt_{}'.format(seton[0])] = 3  # 구매 완료 설정
        # 새로운 주문 완료
    return None


def order_mod_ask3(key1, key2, coinn, profit): #분산형 매도주문 생성
    print("4단계 매도 주문 재생성")
    try:
        cancelaskorder(key1, key2, coinn)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit[0] / 100)
        print("재설정 이윤 :", profit[0])
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        setprice = calprice(setprice)
        globals()['mysell_{}'.format(seton[0])] = setprice
        selllimitpr(key1, key2, coinn, setprice, totalvol)
        # 새로운 매도 주문
    except Exception as e:
        print('매도주문 갱신 에러 ',e)
    finally:
        print('매도주문 갱신')
        globals()['tcnt_{}'.format(seton[0])] = 3  # 구매 완료 설정
        # 새로운 주문 완료
    return None


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


cnt = 1
setons = dbconn.getseton()
for seton in setons:
    globals()['lcnt_{}'.format(seton[0])] = 0  #거래단계 초기화
    globals()['bcnt_{}'.format(seton[0])] = 0  #점검횟수 초기화
    globals()['tcnt_{}'.format(seton[0])] = 0  # 거래 예약 횟수 초기화
    globals()['askcnt_{}'.format(seton[0])] = 0  # 매도거래 수
    globals()['bidcnt_{}'.format(seton[0])] = 0  # 매수거래 수
    globals()['mysell_{}'.format(seton[0])] = 0 #매도 설정 금액

while True:
    print("Run Count : ", cnt)
    try:
        order_cnt_trade(svrno)
        cnt = cnt + 1
    except Exception as e:
        print(e)
    finally:
        time.sleep(1)

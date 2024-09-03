def order_cnt_trade(svrno):
    global orderstat, key1, key2, coinn, askcnt, bidcnt, traded, seton
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
                        if orderstat is None:  #주문 없을때
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
                                order_mod_ask2(keys[0], keys[1], coinn, intRate)  #주문이 있는데 잔고가 있을경우 매도 재설정
                elif globals()['tcnt_{}'.format(seton[0])] == 1:
                    print('1단계 거래')  # 주문 카운트
                    bidcnt1 = 0
                    askcnt1 = 0
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
                    if (myask / myeve * 100 - 100 > intRate[0]):
                        order_mod_ask2(keys[0], keys[1], coinn, intRate)
                        print("금액추적 매도주문 재설정")
                    else:
                        print("주문 금액 비율 :", myask / myeve * 100)
                    # 차이 발생이 일정비율 이상시 재주문

                chkcoin = checktraded(key1, key2, coinn)  # 지갑 점검
                if chkcoin is None:  # 지갑내 해당코인이 없을 경우
                    canclebidorder(key1, key2, coinn)  # 주문 취소
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
        myset = loadmyset(seton)
        uno = myset[1]
        msg = '메인 루프 에러 :'+str(e)
        send_error(msg, uno)
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
        myset = loadmyset(seton)
        uno = myset[1]
        msg = '최초 구매 시작 에러 :'+str(e)
        send_error(msg, uno)
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
        preprice = bidprice  #현재가에 적용
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


def order_new_bid2(key1, key2, coinn, initAsset, intval, intergap, profit):  #고정간격 기법 새구매
    global buyrest, bidasset, bidcnt, askcnt
    print("고정간격 새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset
        buyrest = buymarketpr(key1, key2, coinn, bidasset)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
        globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
    except Exception as e:
        myset = loadmyset(seton)
        uno = myset[1]
        msg = "시장가 구매 2 에러 "+ str(e)
        send_error(msg, uno)
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
        preprice = bidprice  #현재가에 적용
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

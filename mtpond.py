import time
from contextlib import nullcontext
from datetime import datetime
from pyupbit import Upbit
from sqlalchemy.util import await_only
import asyncio
import dbconnmt
import pyupbit
import dotenv
import os
import sys
import requests
import asyncio
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from statsmodels.tsa.arima.model import ARIMA
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


dotenv.load_dotenv()
DATABASE_URL = os.getenv("dburl")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
bidcnt = 1
servtype = "MTPOND"
svrno = os.getenv("server_no")
mainver = 20250727001


async def loadmyset(uno):
    global mysett
    try:
        mysett = await dbconnmt.getmsetup(uno)
    except Exception as e:
        msg = "나의 세팅 조회 에러 " + str(e)
        await send_error(msg, uno)
    finally:
        return mysett


async def buymarketpr(key1, key2, coinn, camount, uno):
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.buy_market_order(coinn, camount)
        return orders
    except Exception as e:
        msg = "시장가 구매 명령 에러 " + str(e)
        await send_error(msg, uno)


async def buylimitpr(key1, key2, coinn, setpr, setvol, uno):
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.buy_limit_order(coinn, setpr, setvol)
        return orders
    except Exception as e:
        msg = "지정가 구매 명령 에러 " + str(e)
        await send_error(msg, uno)


async def selllimitpr(key1, key2, coinn, setpr, setvol, uno):
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.sell_limit_order(coinn, setpr, setvol)
        print("지정가 매도 주문 내용 : ", orders)
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
            await dbconnmt.insertLog(uno, ldata01, ldata02, ldata03, ldata04, ldata05, ldata06, ldata07, ldata08, ldata09,ldata10, ldata11, ldata12, ldata13, ldata14, ldata15, ldata16)
            return orders
    except Exception as e:
        msg = "지정가 매도 에러 " + str(e)
        await send_error(msg, uno)

async def checktraded(key1, key2, coinn, uno):
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
        await send_error(msg, uno)


def get_tick_size(price):
    if price >= 2000000:
        return 1000
    elif price >= 1000000:
        return 500
    elif price >= 500000:
        return 100
    elif price >= 100000:
        return 50
    elif price >= 10000:
        return 10
    elif price >= 1000:
        return 1
    elif price >= 100:
        return 0.1
    elif price >= 10:
        return 0.01
    elif price >= 1:
        return 0.001
    else:
        return 0.0001


def get_tick_size2(price):
    if price >= 2000000:
        return 1000
    elif price >= 1000000:
        return 500
    elif price >= 500000:
        return 100
    elif price >= 100000:
        return 50
    elif price >= 10000:
        return 10
    elif price >= 1000:
        return 1
    elif price >= 100:
        return 1
    elif price >= 10:
        return 0.01
    elif price >= 1:
        return 0.001
    else:
        return 0.0001


async def calprice(bidprice, uno):
    try:
        ticksize = get_tick_size(bidprice)
        bidprice = round(bidprice / ticksize) * ticksize
        return bidprice
    except Exception as e:
        msg = "주문 가격 산출 에러 " + str(e)
        await send_error(msg, uno)


async def calprice2(bidprice, uno):
    try:
        ticksize = get_tick_size2(bidprice)
        bidprice = round(bidprice / ticksize) * ticksize
        return bidprice
    except Exception as e:
        msg = "주문 가격 산출 에러 " + str(e)
        await send_error(msg, uno)


async def cancelaskorder(key1, key2, coinn, uno):  # 매도 주문 취소
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn)
        if orders is not None:
            for order in orders:
                if order['side'] == 'ask':
                    upbit.cancel_order(order["uuid"])
                    await dbconnmt.modifyLog(order["uuid"], "cancelled")
                else:
                    print("매수 주문 유지")
        else:
            pass
    except Exception as e:
        msg = '매도주문취소 에러 ' + str(e)
        await send_error(msg, uno)


async def canclebidorder(key1, key2, coinn, uno):  # 청산
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn)
        if orders is not None:
            for order in orders:
                if order['side'] == 'bid':
                    upbit.cancel_order(order["uuid"])
                else:
                    print("매도 주문 유지")
        else:
            pass
    except Exception as e:
        msg = '매수주문취소 에러 :' + str(e)
        await send_error(msg, uno)


async def order_mod_ask5(key1, key2, coinn, profit, uno):  # 이윤 변동식 계산 방식
    try:
        print("매도 주문 재생성 시작")
        await cancelaskorder(key1, key2, coinn, uno)  # 기존 매도 주문 취소
        tradednew = await checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(
            tradednew['avg_buy_price'])  # 전체 구매 금액
        if totalamt < 5000:
            print("보유금액 5000원 미만으로 추가 구매후 매도")
            await buymarketpr(key1, key2, coinn, 5000, uno)  # 1만원 추가 구매
            totalamt = (float(tradednew['balance']) + float(tradednew['locked'])) * float(tradednew['avg_buy_price'])  # 전체 구매 금액
        totalvol = float(tradednew['balance']) + float(tradednew['locked'])  # 전체 구매 수량
        totalamt = totalamt + (totalamt * profit / 100)
        print("재설정 이윤 :", str(profit))
        print(totalamt)
        print(totalvol)
        setprice = totalamt / totalvol
        if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS", "KRW-GRT",
                     "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI", "KRW-STG", "KRW-TRX"]:
            setprice = await calprice2(setprice, uno)
        else:
            setprice = await calprice(setprice, uno)
        await selllimitpr(key1, key2, coinn, setprice, totalvol, uno)
        # 새로운 매도 주문
    except Exception as e:
        msg = '매도주문5 갱신 에러 ' + str(e)
        await send_error(msg, uno)


async def add_new_bid(key1, key2, coinn, bidprice, bidvol, uno):
    try:
        result = await buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        return result
    except Exception as e:
        msg = "추가매수 진행 에러 " + str(e)
        await send_error(msg, uno)


async def first_trade(key1, key2, coinn, initAsset, intergap, profit, uno):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset  # 매수 금액
        buyrest = await buymarketpr(key1, key2, coinn, bidasset, uno)  # 첫번째 설정 구매
        print("시장가 구매", str(buyrest))
        await asyncio.sleep(0.5)
    except Exception as e:
        msg = '시장가 구매 에러 ' + str(e)
        await send_error(msg, uno)
        print(msg)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = await checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        setprice = float(traded["avg_buy_price"]) * (1.0 + (profit / 100.0))
        if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS", "KRW-GRT",
                     "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI", "KRW-STG", "KRW-TRX"]:
            setprice = await calprice2(setprice, uno)
        else:
            setprice = await calprice(setprice, uno)
        setvolume = traded['balance']
        await selllimitpr(key1, key2, coinn, setprice, setvolume, uno)
        print("1단계 매도 실행 완료")
        # 추가 예약 매수 실행
        bidprice = preprice * (1.00 - (intergap / 100.0))
        if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS", "KRW-GRT",
                     "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI", "KRW-STG", "KRW-TRX"]:
            bidprice = await calprice2(bidprice, uno)
        else:
            bidprice = await calprice(bidprice, uno)
        bidasset = bidasset * 2
        bidvol = bidasset / bidprice
        await buylimitpr(key1, key2, coinn, bidprice, bidvol, uno)
        print("1단계 매수 실행 완료")


async def each_trade(key1, key2, coinn, initAsset, profit, uno):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset + 1000  # 매수 금액
        buyrest = await buymarketpr(key1, key2, coinn, bidasset, uno)  # 첫번째 설정 구매
        print("시장가 구매", str(buyrest))
        await asyncio.sleep(0.1)
    except Exception as e:
        msg = '시장가 구매 에러 ' + str(e)
        await send_error(msg, uno)
        print(msg)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = await checktraded(key1, key2, coinn, uno)  # 설정 코인 지갑내 존재 확인
        setprice = float(preprice) * (1.0 + (profit / 100.0))
        if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS", "KRW-GRT",
                     "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI", "KRW-STG", "KRW-TRX"]:
            setprice = await calprice2(setprice, uno)
        else:
            setprice = await calprice(setprice, uno)
        setvolume = traded['balance']
        await selllimitpr(key1, key2, coinn, setprice, setvolume, uno)
        print("매도 실행 완료")
    return None

async def trService(svrno):
    global uno
    users = await dbconnmt.getsetonsvr_tr(svrno)
    try:
        for user in users:
            setups = await dbconnmt.getmsetup_tr(user)
            try:
                for setup in setups:  # (658,	23,	10000.0, 9,	1.0, 0.5, KRW-ZETA,	Y, 42, 21, N, 6, N, N, 1000000.0)
                    if setup[7] != "Y":
                        continue  # 구동중이지 않은 경우 통과
                    uno = setup[1]
                    holdcnt = setup[11]
                    amtlimityn = setup[13]
                    amtlimit = setup[14]
                    vcoin = setup[6][4:]
                    keys = await dbconnmt.getupbitkey_tr(uno)  # 키를 받아 오기
                    upbit = pyupbit.Upbit(keys[0], keys[1])
                    mycoins = upbit.get_balances()
                    mywon = 0  # 보유 원화
                    myvcoin = 0  # 보유 코인
                    vcoinprice = 0  # 코인 평균 구매가
                    myrestvcoin = 0  # 잔여 코인
                    vcoinamt = 0  # 코인 구매금액
                    bidprice = 0
                    amt = 0
                    amtb = 0
                    addamt = 0
                    addamtb = 0
                    prgap = 0
                    cnt = 0
                    cntb = 0
                    calamt = 0
                    bcoinprice = 0
                    ordtype = 0  # 주문 종류
                    for coin in mycoins:
                        if coin["currency"] == "KRW":
                            mywon = float(coin["balance"])
                            print("KRW", mywon)
                        if coin["currency"] == vcoin:
                            myvcoin = float(coin["balance"]) + float(coin["locked"])
                            myrestvcoin = float(coin["balance"])
                            vcoinprice = float(coin["avg_buy_price"])
                            vcoinamt = myvcoin * vcoinprice
                            print(str(vcoin), ":", str(myvcoin), "Price :", str(vcoinprice))
                    coinn = "KRW-" + vcoin
                    curprice = pyupbit.get_current_price(coinn)
                    print("코인 현재 시장가", str(curprice))
                    print("최초 매수 설정 금액 ", str(setup[2]))
                    print("매수 손실금", curprice - vcoinprice)
                    if isinstance(curprice, (int, float)):
                        if vcoinprice != 0:
                            lcrate = (curprice - vcoinprice) / vcoinprice * 100
                        else:
                            lcrate = 0
                    else:
                        send_error("TRACE 프로세서 실행중 현재가 불러오기 에러", uno)
                        continue
                    print("손실 비율 ", lcrate)
                    myorders = upbit.get_order(coinn, state='wait')  # 대기중 주문 조회
                    cntask = 0  # 매도 주문수
                    cntbid = 0  # 매수 주문수
                    lastbidsec = 0  # 최종 주문 시간
                    if myorders is not None:
                        for order in myorders:
                            nowt = datetime.now()
                            if order["side"] == "ask":
                                cntask = cntask + 1  # 매도 주문수 카운트
                                last = order["created_at"]
                                last = last.replace("T", " ")
                                last = last[:-6]
                                last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                                lastbidsec = (nowt - last).seconds
                            elif order["side"] == "bid":
                                cntbid = cntbid + 1  # 매수 주문 수 카운트
                                bcoinprice = order["price"]  # 주문 가격
                    else:  # 둘다 없을때 0으로 설정
                        cntask = 0
                        cntbid = 0
                    cntpost = 0  # 매수 회차 산출 프로세스
                    print("현재 매도주문수 ", str(cntask))
                    print("현재 매수주문수 ", str(cntbid))
                    # 상세 설정
                    trsets = await dbconnmt.setdetail_tr(setup[8])  # 상세 투자 설정 Trace 로 설정 변경
                    mrate = float(setup[2] / 10000)
                    gapsz = trsets[3:13]
                    intsz = trsets[13:23]
                    netsz = trsets[23:33]
                    netsz = [netsz[i] * mrate for i in range(0, len(netsz))]
                    limsz = trsets[33:43]
                    limsz = [limsz[k] * mrate for k in range(0, len(limsz))]
                    netyn = trsets[43:53]
                    for order in myorders:
                        if order['side'] == 'ask':
                            amt = vcoinamt  # 기존 보유 금액
                            print("기존 보유 금액 ", str(amt))
                            cntpost = 1  # 회차 계산
                            for lim in limsz:
                                if amt >= float(lim):
                                    cntpost += 1
                                else:
                                    continue
                        elif order['side'] == 'bid':
                            amtb = float(order['volume']) * float(order['price'])
                            print("기존 매수 주문 금액 ", str(amtb))
                            print("기존 매수 주문 단가 ", str(order['price']))
                            bdrate = (float(curprice) - float(order['price'])) / float(curprice)
                            print("매수가와 현재가 비율 :", str(bdrate))
                        else:
                            print("기존 매수 없음")
                        if cntpost > 10:  # 최대 구매 상태 도달
                            cntpost = 10
                            if vcoinamt >= float(limsz[cntpost - 1]):
                                print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]),
                                      " 최종 구매 금액 도달 통과")
                                print("------------------------")
                                continue
                        # 갭체크 후 -3%인 경우 손절 실행
                    if amt == 0:
                        cntpost = 1
                        amt = float(netsz[int(cntpost - 1)])  # 현재 구매 설정 금액
                    if amtb == 0:
                        amtb = 0
                    if addamt == 0:
                        addamt = float(setup[2])
                    print("현재 산출 회차 단계", str(cntpost))
                    print("직전 주문 경과시간 ", str(lastbidsec), "초")
                    # 주문 확인
                    if cntask == 0 and cntbid == 0:  # 신규주문
                        ordtype = 1
                        cnt = 1
                    elif cntask == 0 and cntbid != 0:  # 매도후 매수취소
                        ordtype = 2
                    elif cntask != 0 and cntbid == 0:  # 추가 매수 진행
                        # 홀드 및 신호등 체크 !!!!!
                        if lastbidsec < 2:
                            ordtype = 0
                            print("급격하락 1초 딜레이")
                        else:
                            ordtype = 3
                    else:
                        ordtype = 0  # 기타
                    if cntbid == 0 and cntask == 0:
                        bidprice = float(netsz[int(cntpost - 1)])
                    else:
                        bidprice = float(netsz[int(cntpost - 1)])
                    print("매수 설정 금액 : ", str(bidprice))
                    # 다음 투자금 확인
                    intvset = 0
                    marginset = 0
                    bidintv = gapsz[int(cntpost - 1)]  # 간격 설정
                    bidmargin = intsz[int(cntpost - 1)]  # 이윤 설정
                    if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS", "KRW-GRS",
                                 "KRW-GRT", "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL", "KRW-SAND", "KRW-SEI",
                                 "KRW-STG", "KRW-TRX"]:
                        bideaprice = calprice2(float(curprice * (1 - bidintv / 100)), uno)  # 목표 단가
                    else:
                        bideaprice = calprice(float(curprice * (1 - bidintv / 100)), uno)  # 목표 단가
                    bidvolume = float(bidprice) / float(bideaprice)
                    print("매수설정단가 ", str(bideaprice))
                    print("매수설정개수 ", str(bidvolume))
                    print("설정회차", str(cntpost))
                    print("설정금액", str(bidprice))
                    print("설정간격", str(bidintv))
                    print("설정이윤", str(bidmargin))
                    print("구매한계 금액", str(amtlimit))
                    if amtlimityn == "Y":
                        activeamt = float(amt) + float(amtb)
                        if activeamt >= amtlimit:
                            print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]),
                                  " 구매 한계 금액 도달 통과")
                            print("------------------------")
                            if myrestvcoin != 0:
                                print("잔여 코인 존재: ", myrestvcoin)
                                order_mod_ask5(keys[0], keys[1], coinn, bidmargin, uno)
                                print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]), " 매도 재주문")
                                print("------------------------")
                            await asyncio.sleep(0.1)
                            continue
                    else:
                        print("구매한계 금액 설정 없음")
                    if float(setup[4]) == 1.0:
                        # 손절 실행
                        if lcrate <= float(setup[5]):
                            if cntpost < 10 and mywon < bidprice:
                                try:
                                    print("손절 적용 조건 진입 : 손절 조건 (자금 부족)", setup[5])
                                    losscut(uno, coinn, lcrate, mywon)
                                    print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]),
                                          " 손절 조건에 따른 손절 실행")
                                    if setup[12] == 'Y':
                                        print("손절 후 자동 멈춤 실행")
                                        await dbconnmt.setonoff(str(setup[0]), 'N')
                                except Exception as e:
                                    print("손절 적용 에러 ", e)
                                finally:
                                    print("손절 적용 완료")
                                    continue
                            elif cntpost == 10:  # 최종 단계 도달
                                try:
                                    print("손절 적용 조건 진입 : 손절 조건 (최대 매입)", setup[5])
                                    losscut(uno, coinn, lcrate, mywon)
                                    print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]),
                                          " 손절 조건에 따른 손절 실행")
                                    if setup[12] == 'Y':
                                        print("손절 후 자동 멈춤 실행")
                                        await dbconnmt.setonoff(str(setup[0]), 'N')
                                except Exception as e:
                                    print("손절 적용 에러 ", e)
                                finally:
                                    print("손절 적용 완료")
                                    continue
                            else:
                                print("손절 조건 통과 손절하지 않음!!")
                    else:
                        print('손절 기능 비활성화')
                    if myrestvcoin != 0:
                        print("잔여 코인 존재: ", myrestvcoin)
                        order_mod_ask5(keys[0], keys[1], coinn, bidmargin, uno)
                        print("TR사용자 ", str(setup[1]), "설정번호 ", str(setup[0]), " 코인 ", str(setup[6]), " 매도 재주문")
                        print("------------------------")
                        await asyncio.sleep(0.1)
                        continue
                    if ordtype == 1:
                        print("주문실행 설정", str(ordtype))
                        if mywon >= bidprice:
                            await each_trade(keys[0], keys[1], coinn, bidprice, bidmargin, uno)
                        else:
                            print("현금 부족으로 1차 주문 패스 (보유현금 :", str(mywon), ")")
                    elif ordtype == 2:
                        print("주문실행 설정", str(ordtype))
                        await canclebidorder(keys[0], keys[1], coinn, uno)
                    elif ordtype == 3:
                        print("주문실행 설정", str(ordtype))
                        cntpr = int(cntpost - 1)
                        cntnx = int(cntpost)
                        if cntnx >= 10:
                            cntnx = 10
                        needmon = float(limsz[cntnx - 1]) - float(limsz[cntpr - 1])  # 필요현금
                        settimes = float(needmon) / float(netsz[cntpr])  # 반복회수
                        # 보유 현금이 충분할 경우만 실행
                        if netyn[cntpr] == 'Y':
                            bidcalprice = bideaprice
                            print("네트타입 구매")
                            for i in range(int(settimes)):
                                if i == 0:
                                    await add_new_bid(keys[0], keys[1], coinn, bideaprice, bidvolume, uno)
                                else:
                                    if coinn in ["KRW-ADA", "KRW-ALGO", "KRW-BLUR", "KRW-CELO", "KRW-ELF", "KRW-EOS",
                                                 "KRW-GRS", "KRW-GRT", "KRW-ICX", "KRW-MANA", "KRW-MINA", "KRW-POL",
                                                 "KRW-SAND", "KRW-SEI",
                                                 "KRW-STG", "KRW-TRX"]:
                                        bidcalprice = calprice2(float(bidcalprice * (1 - bidintv / 100)), uno)  # 목표 단가
                                    else:
                                        bidcalprice = calprice(float(bidcalprice * (1 - bidintv / 100)), uno)  # 목표 단가
                                    bidvol = float(netsz[cntpr]) / float(bidcalprice)
                                    await add_new_bid(keys[0], keys[1], coinn, bidcalprice, bidvol, uno)
                        else:
                            print("단일 구매")
                            if mywon >= bidprice:
                                await add_new_bid(keys[0], keys[1], coinn, bideaprice, bidvolume, uno)
                            else:
                                print("현금 부족으로 추가 주문 패스 (보유현금 :", str(mywon), ")")
                    else:
                        print("이번 회차 주문 설정 없음")
                    # 주문 기록
                    print("TR사용자 ", str(setup[1]), "Trace 설정번호 ", str(setup[0]), " 코인 ", str(setup[6]), " 정상 종료")
                    print("------------------------")
                    await asyncio.sleep(0.1)
            except Exception as e:
                msg = "TR사용자 " + str(setup[1]) + "설정번호 " + str(setup[0]) + " 코인 " + str(setup[6]) + " 에러 " + str(e)
                print(msg)
                await send_error(msg, uno)
                continue
    except Exception as e:
        msg = "구간 루프 에러 :" + str(e)
        await send_error(msg, uno)
        print("구간 루프 에러 :", e)
    finally:
        ntime = datetime.now()
        print('TRTRTRTRTRTRTRTRTRTRTRTRTRTRTR')
        print('거래점검 시간', str(ntime))
        print('점검 서버', str(svrno))
        print('서비스 버전', str(mainver))
        print('TRTRTRTRTRTRTRTRTRTRTRTRTRTRTR')
        await dbconnmt.clearcache()  # 캐쉬 삭제


async def mtpondService(uno):
    try:
        setcoins = []
        setups = await dbconnmt.getmsetup_tr(uno) # 사용자별 설정 로드
        # 1. setcoins를 한 번에 모으기
        for setup in setups:
            if setup[7] == 'Y':
                setcoins.append(setup[6])
        # 2. setcoins가 비었으면 통과
        if not setcoins:
            print('설정된 코인이 없어 사용자', uno, '통과')
        else:
            # 3. setcoins에 대해 한 번만 루프
            for setcoin in setcoins:
                print("실행 코인", setcoin)
                await asyncio.sleep(1)
        print("사용자", uno, "설정실행 완료")
    except Exception as e:
        msg = "서비스 MTPond 메인 루프 에러 : " + str(e)
        await send_error(msg, svrno)
    finally:
        ntime = datetime.now()
        print('mtmtmtmtmtmtmtmtmtmtmtmtmtmtmtmt')
        print('거래점검 시간', str(ntime))
        print('점검 서버', str(svrno))
        print('서비스 버전', str(mainver))
        print('사용자 ', str(uno))
        print('mtmtmtmtmtmtmtmtmtmtmtmtmtmtmtmt')


async def service_restart():
    tstamp = datetime.now()
    print("Service Restart : ", tstamp)
    try:
        myip = (requests.get('https://api.ip.pe.kr/json/').json())['ip']
    except Exception as e:
        myip = "0.0.0.0"
    msg = "Server " + str(svrno) + " Service Restart : " + str(tstamp) + "  at  " + str(myip) + " Service Ver : " + str(
        mainver) + ":" + str(servtype)
    await send_error(msg, '0')
    await dbconnmt.serviceStat(svrno, myip, mainver)
    os.execl(sys.executable, sys.executable, *sys.argv)


async def service_start():
    tstamp = datetime.now()
    print("Service Start : ", tstamp)
    try:
        myip = (requests.get('https://api.ip.pe.kr/json/').json())['ip']
    except Exception as e:
        myip = "0.0.0.0"
    msg = "Multi Server " + str(svrno) + " Service Start : " + str(tstamp) + "  at  " + str(
        myip) + " Service Ver : " + str(mainver) + ":" + str(servtype)
    vermsg = str(mainver) + ":" + str(servtype)
    await dbconnmt.servicelog(msg, 0)
    await dbconnmt.serviceStat(svrno, myip, vermsg)
    os.system("pip install -r ./requirement.txt")


async def send_error(err, uno):
    await dbconnmt.errlog(err, uno)


async def get_lastbuy(key1, key2, coinn, uno):
    global lastbuy
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn, state='wait')
        lastbuy = await dbconnmt.getlog(uno, 'BID', coinn)
        if lastbuy is None:
            lastbuy = datetime.now()
        for order in orders:  # 내용이 있을 경우 업데이트
            if order["side"] == 'bid':
                last = order["created_at"]
                last = last.replace("T", " ")
                last = last[:-6]
                last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if last != lastbuy:
                    await dbconnmt.tradelog(uno, "BID", coinn, last)
                    lastbuy = await dbconnmt.getlog(uno, 'BID', coinn)
    except Exception as e:
        msg = "최근 거래 조회 에러 : " + str(e)
        await send_error(msg, uno)
    finally:
        return lastbuy


async def get_lasttrade(key1, key2, coinn, uno):
    global lasthold
    try:
        upbit = pyupbit.Upbit(key1, key2)
        orders = upbit.get_order(coinn, state='done', limit=1)
        lasthold = await dbconnmt.getlog(uno, 'HOLD', coinn)
        if lasthold is None:
            lasthold = datetime.now()
        for order in orders:
            if order["side"] == 'bid':
                last = order["created_at"]
                last = last.replace("T", " ")
                last = last[:-6]
                last = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if last != lasthold:
                    await dbconnmt.tradelog(uno, "HOLD", coinn, last)
    except Exception as e:
        msg = "최종 거래 점검 에러 : " + str(e)
        await send_error(msg, uno)
    finally:
        lasthold = await dbconnmt.getlog(uno, 'HOLD', coinn)[0]
        return lasthold


async def chk_lastbid(coinn, uno, restmin):
    now = datetime.now()
    lastbid = await dbconnmt.getlog(uno, 'BID', coinn)[0]
    lastbid = str(lastbid)
    if lastbid != None:
        past = datetime.strptime(lastbid, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        print("구매 경과 시간 :", str(diffmin), "분")
        if diffmin <= restmin:
            return "DELAY"
        else:
            return "SALE"
    else:
        print("직전 구매 이력 없음")


async def losscut(uno, coinn, gap, mywon):
    keys = await dbconnmt.getupbitkey_tr(uno)
    await cancelaskorder(keys[0], keys[1], coinn, uno)  # 기존 매도주문 취소
    upbit = pyupbit.Upbit(keys[0], keys[1])
    walt = upbit.get_balances()
    crp = pyupbit.get_current_price(coinn)
    vcoin = coinn[4:]
    for coin in walt:
        if coin['currency'] == vcoin:
            balance = coin['balance']
            lcgap = (float(crp) - float(coin['avg_buy_price'])) / float(coin['avg_buy_price'])
            lossamt = (float(crp) - float(coin['avg_buy_price'])) * float(balance)
            lcamt = float(crp) * float(balance)
            result = upbit.sell_market_order(coinn, balance)
            if result is not None:
                await dbconnmt.lclog(coinn, uno, lcgap, lcamt, mywon, lossamt)
        else:
            pass


async def save_holdtime(uno, coinn):
    await dbconnmt.tradelog(uno, 'HOLD', coinn)


async def check_hold(min, uno, coinn):
    now = datetime.now()
    last = await dbconnmt.getlog(uno, 'HOLD', coinn)[0]
    last = str(last)
    if last != None:
        past = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
        diff = now - past
        diffmin = diff.seconds / 60
        print("경과시간 : ", str(diffmin), "분")
        if diffmin <= min:
            return "HOLD"
        else:
            return "SALE"
    else:
        await dbconnmt.tradelog(uno, 'HOLD', coinn)  # 구매 카운트 시작


async def check_holdstart(min, uno, coinn):  # 홀드시작이후 시간 체크
    now = datetime.now()
    last = await dbconnmt.getlog(uno, 'HOLD', coinn)[0]
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
        await save_holdtime(uno, coinn)  # 새로운 홀드 카운트 시작


async def main_loop():
    cnt = 1
    servt = await dbconnmt.getserverType(svrno)
    users = await dbconnmt.getsetonsvr_tr(svrno) # 서버에 속한 사용자 확인
    servtype = servt[0]
    serveryn = servt[1]
    if servtype is None:
        servtype = "MTPOND"
    if serveryn is None:
        serveryn = "Y"
    await service_start()
    while True:
        print("구동 횟수 : ", str(cnt))
        try:
            if servtype == "MTPOND" and serveryn == 'Y':
                if users:  # 사용자 리스트가 비어있지 않으면
                    for user in users:
                        await mtpondService(user[0])
                else:
                    print("서버에 속한 사용자가 없습니다.")
            elif servtype == "TRACE" and serveryn == 'Y':
                await trService(svrno)
            elif servtype == "EXP":
                print("Not Available Server !!")
            else:
                print("No Server Data !!")
            cnt = cnt + 1
        except Exception as e:
            msg = "메인 while 반복문 에러 : " + str(e)
            await send_error(msg, 0)
        finally:
            await dbconnmt.clearcache()
            if cnt > 3600:  # 0.5시간 마다 재시작
                cnt = 1
                await service_restart()
            servt = await dbconnmt.getserverType(svrno)
            if servt[0] is not None:
                if servtype != servt[0]:
                    await service_restart()


if __name__ == "__main__":
    asyncio.run(main_loop())

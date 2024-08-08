import pyupbit


def get_trend(coinn):
    opoint, cpoint, hpoint, lpoint, vpoint = 0, 0, 0, 0, 0
    trend = []
    try:
        crprice = pyupbit.get_current_price(coinn)
        candls = pyupbit.get_ohlcv(ticker=coinn, interval= "minute1", count=4)
        candls = [candls]
        openpr = candls[0]['open'].tolist()
        closepr = candls[0]['close'].tolist()
        highpr = candls[0]['high'].tolist()
        lowpr = candls[0]['low'].tolist()
        volumepr = candls[0]['volume'].tolist()
        opric, cpric, hpric, lpric, volic = [], [], [], [], []
        for i in range(0,3):
            if openpr[i + 1] > openpr[i]:
                opric.append('+')
                opoint = opoint + 1
            elif openpr[i+1] <= openpr[i]:
                opric.append('-')
                opoint = opoint - 1
            if closepr[i+1] > closepr[i]:
                cpric.append('+')
                cpoint = cpoint + 1
            elif closepr[i+1] <= closepr[i]:
                cpric.append('-')
                cpoint = cpoint - 1
            if highpr[i+1] > highpr[i]:
                hpric.append('+')
                hpoint = hpoint + 1
            elif highpr[i+1] <= highpr[i]:
                hpric.append('-')
                hpoint = hpoint - 1
            if lowpr[i+1] > lowpr[i]:
                lpric.append('+')
                lpoint = lpoint + 1
            elif lowpr[i+1] <= lowpr[i]:
                lpric.append('-')
                lpoint = lpoint - 1
            if volumepr[i+1] > volumepr[i]:
                volic.append('+')
                vpoint = vpoint + 1
            elif volumepr[i+1] <= volumepr[i]:
                volic.append('-')
                vpoint = vpoint - 1
        trend = opric
        trend.extend(cpric)
        trend.extend(hpric)
        trend.extend(lpric)
        trend.extend(volic)
    except Exception as e:
        print("Trend check Error ", e)
    finally:
        return trend, opoint+cpoint+hpoint+lpoint, vpoint


def get_trend4h(coinn):
    opoint4h, cpoint4h, hpoint4h, lpoint4h, vpoint4h = 0, 0, 0, 0, 0
    trend4h = []
    try:
        crprice = pyupbit.get_current_price(coinn)
        candls4h = pyupbit.get_ohlcv(ticker=coinn, interval= "minute60", count=4)
        candls4h = [candls4h]
        openpr4h = candls4h[0]['open'].tolist()
        closepr4h = candls4h[0]['close'].tolist()
        highpr4h = candls4h[0]['high'].tolist()
        lowpr4h = candls4h[0]['low'].tolist()
        volumepr4h = candls4h[0]['volume'].tolist()
        opric4h, cpric4h, hpric4h, lpric4h, volic4h = [], [], [], [], []
        for i in range(0,3):
            if openpr4h[i + 1] > openpr4h[i]:
                opric4h.append('+')
                opoint4h = opoint4h + 1
            elif openpr4h[i+1] <= openpr4h[i]:
                opric4h.append('-')
                opoint4h = opoint4h - 1
            if closepr4h[i+1] > closepr4h[i]:
                cpric4h.append('+')
                cpoint4h = cpoint4h + 1
            elif closepr4h[i+1] <= closepr4h[i]:
                cpric4h.append('-')
                cpoint4h = cpoint4h - 1
            if highpr4h[i+1] > highpr4h[i]:
                hpric4h.append('+')
                hpoint4h = hpoint4h + 1
            elif highpr4h[i+1] <= highpr4h[i]:
                hpric4h.append('-')
                hpoint4h = hpoint4h - 1
            if lowpr4h[i+1] > lowpr4h[i]:
                lpric4h.append('+')
                lpoint4h = lpoint4h + 1
            elif lowpr4h[i+1] <= lowpr4h[i]:
                lpric4h.append('-')
                lpoint = lpoint4h - 1
            if volumepr4h[i+1] > volumepr4h[i]:
                volic4h.append('+')
                vpoint4h = vpoint4h + 1
            elif volumepr4h[i+1] <= volumepr4h[i]:
                volic4h.append('-')
                vpoint4h = vpoint4h - 1
        trend4h = opric4h
        trend4h.extend(cpric4h)
        trend4h.extend(hpric4h)
        trend4h.extend(lpric4h)
        trend4h.extend(volic4h)
    except Exception as e:
        print("Trend4h check Error ", e)
    finally:
        return trend4h, opoint4h+cpoint4h+hpoint4h+lpoint4h, vpoint4h, crprice


def get_trendnew(coinn):
    opoint4h, cpoint4h, hpoint4h, lpoint4h, vpoint4h = 0, 0, 0, 0, 0
    trend4h = []
    try:
        crprice = pyupbit.get_current_price(coinn)
        candls4h = pyupbit.get_ohlcv(ticker=coinn, interval= "minute15", count=10)
        candls4h = [candls4h]
        openpr4h = candls4h[0]['open'].tolist()
        closepr4h = candls4h[0]['close'].tolist()
        highpr4h = candls4h[0]['high'].tolist()
        lowpr4h = candls4h[0]['low'].tolist()
        volumepr4h = candls4h[0]['volume'].tolist()
        opric4h, cpric4h, hpric4h, lpric4h, volic4h = [], [], [], [], []
        print(openpr4h)
        print(closepr4h)
        for i in range(0, 9):
            gap = closepr4h[i] - openpr4h[i]
            avg = (closepr4h[i] + openpr4h[i])/2
            grate = round(gap/avg*100, 3)
            print(gap, grate)

    except Exception as e:
        print("Trend4h check Error ", e)
    finally:
        return None


trend = get_trendnew("KRW-XRP")
print(trend)
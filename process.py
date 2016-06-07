import datetime 
import csv 
from urllib.request import urlopen 
from urllib.parse import quote_plus 
import logging 

def day_value(info, max_value): 
    day = 0 
    for row_info in info:
        if row_info > max_value: 
            day = day + 1 
    return day 

def day_MFI(data, window=10): 
    try: 
        import numpy as np
        weight = np.ones((window,)) / window 
        close = np.array(data['close']) 
        low = np.array(data['low']) 
        high = np.array(data['high']) 
        volume = np.array(data['volume']) 
        clv = ((close - low) - (high - close)) / (high - low) * volume 
        mfi = [] 
        pred_clv_i = 0 
        for clv_i in clv: 
            mfi.append(pred_clv_i + clv_i)
        weight = np.exp(np.linspace(-1., 0., window)) 
        weight /= weight.sum() 
        ema = np.convolve(mfi, weight)[:len(data['close'])]
        ema = ema[window:]
        mfi = mfi[window:]
    except ImportError: 
        logging.error('Библиотека Numpy не найдена') 
    dates = data['date'][window:]
    data = {
        'date': dates,
        'ema': ema, 
        'mfi': mfi, 
        'table': {date: {'ema': ema[i], 'mfi': mfi[i]} for i, date in enumerate(dates)}, 
        'columns': ['ema', 'mfi'] 
        }
    return data 

def ema_signals(data, ema):
    result = {}
    pred_indicator_mfi = None 
    pred_indicator_ema = None 
    
    for date in sorted(ema['table'].keys()): 
        indicator_ema = ema['table'][date]['ema'] 
        indicator_mfi = ema['table'][date]['mfi']
        if pred_indicator_mfi == None: 
            pred_indicator_mfi = indicator_mfi 
            pred_indicator_ema = indicator_ema 
        if (indicator_mfi > indicator_ema) and (pred_indicator_mfi < pred_indicator_ema):
            result[date] = {'signal': 'BUY'} 
        elif (indicator_mfi < indicator_ema) and (pred_indicator_mfi > pred_indicator_ema):
            result[date] = {'signal': 'SELL'} 
        pred_indicator_mfi = indicator_mfi 
        pred_indicator_ema = indicator_ema 
    return { 
        'table': result, 
        'text_columns': ['signal'] 
    } 

def print_file(file_out, rezult): 
    if file_out: 
        with open(file_out, 'w') as f_out: 
            f_out.write(str(rezult)) 
    print(rezult) 

def print_file_signal(file_out, data, width=15):
    row_format = '{date!s:^{width}}' 
    if file_out: 
        with open(file_out, 'w') as f_out: 
            for date in sorted(data['table'].keys()): 
                f_out.write(row_format.format(date=date, **data['table'][date], width=width) + data['table'][date]['signal'] + '\n') 
                print(row_format.format(date=date, **data['table'][date], width=width) + data['table'][date]['signal']) 
                

def read_url(symbol, year): 
    start = datetime.date(year, 1, 1) 
    end = datetime.date(year, 12, 31) 
    url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv" 
    url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y'))) 
    
    data = urlopen(url).readlines() 
    
    info = { 
        'date': [], 
        'open': [], 
        'close': [], 
        'high': [], 
        'low': [], 
        'volume': [], 
        'table': {}, # Для хранения данных по строкам 
        #информация колонках 
        'columns': ['open', 'close', 'high', 'low', 'volume'] 
    } 
    
    for line in data[1:]: # Пропускаем первую строку с именами колонок 
        row = line.decode().strip().split(',') 
        date = datetime.datetime.strptime(row[0], '%d-%b-%y').date() 
        open_price = float(row[1]) 
        close_price = float(row[2]) 
        high_price = float(row[3]) 
        low_price = float(row[4]) 
        volume_price = float(row[5])
        info['date'].append(date) 
        info['open'].append(open_price) 
        info['close'].append(close_price) 
        info['high'].append(high_price) 
        info['low'].append(low_price) 
        info['volume'].append(volume_price) 
        info['table'][date] = { 
            'open': open_price, 
            'close': close_price, 
            'high': high_price, 
            'low': low_price, 
            'volume': volume_price, 
        } 
        
    return info 

def read_file(file): 
    info = { 
        'date': [], 
        'open': [], 
        'close': [], 
        'high': [], 
        'low': [],
        'volume': [], 
        'table': {}, # Для хранения данных по строкам 
        #информация колонках 
        'columns': ['open', 'close', 'high', 'low', 'volume'] 
    } 
    with open(file) as f: 
        f.readline() 
        csv_file = csv.reader(f, delimiter=',') 
        close_prices = [] 
        for row in csv_file:
            date = row[0] 
            open_price = float(row[1]) 
            close_price = float(row[4]) 
            high_price = float(row[2]) 
            low_price = float(row[3]) 
            volume_price = float(row[5]) 
            info['date'].append(date) 
            info['open'].append(open_price) 
            info['close'].append(close_price) 
            info['high'].append(high_price) 
            info['low'].append(low_price) 
            info['volume'].append(volume_price) 
            info['table'][date] = { 
                'open': open_price, 
                'close': close_price, 
                'high': high_price, 
                'low': low_price, 
                'volume': volume_price, 
                } 
    return info 


def process_data(data, up_value, file_out, indicator): 
    if indicator is None: 
        day = day_value(data["volume"], up_value) 
        print_file(file_out, day) 
    if indicator == "MFI": 
        ema = day_MFI(data) 
        signals = ema_signals(data, ema)
        print_file_signal(file_out, signals) 

def process_network(symbol, up_value, year, file_out, indicator): 
    data = read_url(symbol, year) 
    process_data(data, up_value, file_out, indicator) 

def process_file(file, up_value, file_out, indicator): 
    data = read_file(file) 
    process_data(data, up_value, file_out, indicator)
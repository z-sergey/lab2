import sys
import csv

def day_up_value(close_prices, max_value):
    day = 0
    for close_price in close_prices:
        if close_price <= max_value: 
            day = day + 1
    return day
    

def main(file_name, max_value, file_name_print=None):
    with open(file_name) as f:
        f.readline()
        csv_file = csv.reader(f, delimiter=',')
        close_prices = []
        for row in csv_file:
            x=float((row[5]))
            close_prices.append(x)
    day = day_up_value(close_prices, max_value)        
    if file_name_print:
        with open(file_name_print, 'w') as f_out:
            f_out.write(str(day))

        #f_out = open(file_name_print, 'w')
        #f_out.write(str(day))
    print(day)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        if len(sys.argv) > 2:
            max_value = sys.argv[2]
            file_name_print = sys.argv[3] if len(sys.argv) > 3 else None
            main(file_name, float(max_value), file_name_print)
        else:
            print("Укажите объем торгов")
    else:    
        print("Укажите имя файла")
        
        import sys
import argparse
import process
import logging

 
def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", help="Биржевой символ акций")
    parser.add_argument("-f","--file", help="Файл для обработки")
    parser.add_argument ("up_value",  help="Максимальный уровень цен", type=int)
    parser.add_argument ("-y", "--year", help="Год", default=2016, type=int)
    parser.add_argument ("-fo", "--file_out", help="Файл для записи результата", default="rezult.txt")
    parser.add_argument ("-fl", "--file_log", help="Файл для логирования", default="app.log")
    parser.add_argument ("-l", "--level_log", help="Уровень логирования", default="INFO")
 
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    if namespace.file:
        logging.basicConfig(filename=namespace.file_log, level=namespace.level_log)
        logging.info('Программа запущена с параметрами ' + str(namespace) + "в режиме файл")
        
        try:
            process.process_file(namespace.file, namespace.up_value, namespace.file_out, namespace.file_log, namespace.level_log) 
        except Exception as e:
            logging.info(str(e))
    elif namespace.symbol:
        logging.basicConfig(filename=namespace.file_log, level=namespace.level_log)
        logging.info('Программа запущена с параметрами ' + str(namespace) + "в режиме сеть")
        try:
            process.process_network(namespace.symbol, namespace.up_value, namespace.year,  namespace.file_out, namespace.file_log, namespace.level_log)
        except Exception as e:
            logging.info(str(e))
            
            import datetime
import csv
from urllib.request import urlopen
from urllib.parse import quote_plus

def day_up_value(close_prices, max_value):
    day = 0
    for close_price in close_prices:
        if close_price > max_value: 
            day = day + 1
    return day
    
def print_file(file_out, rezult):
    if file_out:
        with open(file_out, 'w') as f_out:
            f_out.write(str(rezult))
    print(rezult)

def process_network(symbol, up_value, year, file_out, file_log, level_log):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv"
    url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y')))
    data = urlopen(url).readlines()
    close_prices = []
    for row in data[1:]:
        x=float(row.decode().strip().split(',')[4])
        close_prices.append(x)
    day = day_up_value(close_prices, up_value)
    print_file(file_out, day)
    
def process_file(file, up_value, file_out, file_log, level_log):
    with open(file) as f:
        f.readline()
        csv_file = csv.reader(f, delimiter=',')
        close_prices = []
        for row in csv_file:
            x=float(row[4])
            close_prices.append(x)
    day = day_up_value(close_prices, up_value) 
    print_file(file_out, day)
    
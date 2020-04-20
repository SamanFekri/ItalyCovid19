import requests
from datetime import datetime, timedelta
from threading import Timer
import time


def core():
    # api-endpoint
    URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json"

    # sending get request and saving the response as response object
    r = requests.get(url=URL)
    res = r.json()

    lombardi = {
        'total': {'positive': 0, 'death': 0, 'healed': 0},
        'today': {'positive': 0, 'death': 0, 'healed': 0},
    }
    italy = {
        'total': {'positive': 0, 'death': 0, 'healed': 0},
        'today': {'positive': 0, 'death': 0, 'healed': 0},
    }

    for item in res:
        isToday = datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date() == datetime.today().date()
        isYesterday = datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date() == (
                datetime.today() - timedelta(days=1)).date()
        if item['codice_regione'] == 3:
            if isToday:
                lombardi['today']['positive'] = item['nuovi_positivi']
                lombardi['today']['healed'] = item['dimessi_guariti'] - lombardi['total']['healed']
                lombardi['today']['death'] = item['deceduti'] - lombardi['total']['death']

            lombardi['total']['positive'] += item['nuovi_positivi']
            lombardi['total']['healed'] = item['dimessi_guariti']
            lombardi['total']['death'] = item['deceduti']

        if isToday:
            italy['today']['positive'] += item['nuovi_positivi']

            italy['total']['positive'] += item['totale_positivi']
            italy['total']['healed'] += item['dimessi_guariti']
            italy['total']['death'] += item['deceduti']

        if isYesterday:
            italy['today']['healed'] += item['dimessi_guariti']
            italy['today']['death'] += item['deceduti']

    italy['today']['healed'] = italy['total']['healed'] - italy['today']['healed']
    italy['today']['death'] = italy['total']['death'] - italy['today']['death']
    print("-------------- italy")
    print(italy)
    print("-------------- lombardia")
    print(lombardi)
    print("--------------")

    text = """
    📈 امروز در استان لمباردیا :
    ({date})
    
• فوت شدگان: {death}    
    ({today_death:+})

    • بهبود یافتگان: {healed}
    ({today_healed:+})

    مجموع کیسهای کرونا: {positive}
    ({today_positive:+})

    #آمارروزانه
    #آمار
    🇮🇹 @coronaitaliafarsi
    Powered by [Skings](tg://user?id=82768138)
    """

    text = text.format(
        date=datetime.today().date().strftime("%d/%m/%Y"),
        death=lombardi['total']['death'], today_death=lombardi['today']['death'],
        healed=lombardi['total']['healed'], today_healed=lombardi['today']['healed'],
        positive=lombardi['total']['positive'], today_positive=lombardi['today']['positive']
    )
    print("--------------")
    print(text)

    data = {
        "chat_id": "@coronaitaliafarsi",
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post("https://api.telegram.org/bot<id>/sendMessage", data)

    text = """
    📢📢📢 دولت ایتالیا هر روز ساعت ۱۸ آخرین آمار مبتلایان رو اعلام میکنه:

     📈 آخرین آمار {date}
    
    • فوت شدگان: {death}
    ({today_death:+})
    
    • بهبود یافتگان: {healed}
    ({today_healed:+})
    
    • مجموع کیسهای کرونا: {positive}
    ({today_positive:+})
    #آمارروزانه
    #آمار
    🇮🇹@coronaitaliafarsi
    Powered by [Skings](tg://user?id=82768138)
"""

    text = text.format(
        date=datetime.today().date().strftime("%d/%m/%Y"),
        death=italy['total']['death'], today_death=italy['today']['death'],
        healed=italy['total']['healed'], today_healed=italy['today']['healed'],
        positive=italy['total']['positive'], today_positive=italy['today']['positive']
    )
    print("--------------")
    print(text)
    print("--------------")

    data = {
        "chat_id": "@coronaitaliafarsi",
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post("https://api.telegram.org/bot<id>/sendMessage", data)

while True:
    x = datetime.today()
    y = x.replace(day=x.day, hour=x.hour, minute=x.minute + 1, second=0, microsecond=0)
    delta_t = y - x

    secs = delta_t.seconds + 1

    core()
    time.sleep(secs)

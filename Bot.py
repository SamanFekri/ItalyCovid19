import requests
from datetime import datetime, timedelta
import time
import json

# config = {
#     "first_publish": False,
#     "src": "",
#     "bot": {
#         "url": "",
#         "token": "",
#         "silent": False,
#         "channel_id": ""
#     }
# }
with open('.env.json') as f:
    config = json.load(f)

print("Config loaded")
print(config)
config['bot']['url'] = config['bot']['url'].format(token=config['bot']['token'])


def core():
    # api-endpoint
    URL = config['src']

    # sending get request and saving the response as response object
    r = requests.get(url=URL)
    res = r.json()

    # print(res)

    lombardi = {
        'total': {'positive': 0, 'death': 0, 'healed': 0, 'cur': 0, 'hospitalization': 0, 'severe': 0},
        'today': {'positive': 0, 'death': 0, 'healed': 0, 'cur': 0, 'hospitalization': 0, 'severe': 0},
    }
    italy = {
        'total': {'positive': 0, 'death': 0, 'healed': 0, 'cur': 0, 'hospitalization': 0, 'severe': 0, 'test': 0},
        'today': {'positive': 0, 'death': 0, 'healed': 0, 'cur': 0, 'hospitalization': 0, 'severe': 0, 'test': 0},
        'yesterday': {'positive': 0, 'test': 0}
    }

    duplicate_detector = {'Today': {}, 'Yesterday': {}}

    for item in res:
        isToday = datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date() == (
                datetime.today() - timedelta(days=0)).date()
        isYesterday = datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date() == (
                datetime.today() - timedelta(days=1)).date()
        is2DaysAgo = datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date() == (
                datetime.today() - timedelta(days=2)).date()
        # print(datetime.strptime(item['data'], '%Y-%m-%dT%H:%M:%S').date(), (datetime.today() - timedelta(days=1)).date())

        if item['codice_regione'] == 3:
            if isToday:
                lombardi['today']['positive'] = item['nuovi_positivi']
                lombardi['today']['healed'] = item['dimessi_guariti'] - lombardi['total']['healed']
                lombardi['today']['death'] = item['deceduti'] - lombardi['total']['death']

            lombardi['total']['positive'] += item['nuovi_positivi']
            lombardi['total']['healed'] = item['dimessi_guariti']
            lombardi['total']['death'] = item['deceduti']

        if isToday:
            if (item['denominazione_regione'] in duplicate_detector['Today']):
                continue
            duplicate_detector['Today'][item['denominazione_regione']] = 1

            italy['today']['positive'] += item['nuovi_positivi']
            italy['total']['healed'] += item['dimessi_guariti']
            italy['total']['death'] += item['deceduti']
            italy['total']['hospitalization'] += item['ricoverati_con_sintomi']
            italy['total']['severe'] += item['terapia_intensiva']
            italy['total']['test'] += item['tamponi_test_molecolare'] + item['tamponi_test_antigenico_rapido']

            print(item)

        if isYesterday:
            if (item['denominazione_regione'] in duplicate_detector['Yesterday']):
                continue
            duplicate_detector['Yesterday'][item['denominazione_regione']] = 1

            italy['today']['healed'] += item['dimessi_guariti']
            italy['today']['death'] += item['deceduti']
            italy['today']['hospitalization'] += item['ricoverati_con_sintomi']
            italy['today']['severe'] += item['terapia_intensiva']
            italy['today']['test'] += item['tamponi_test_molecolare'] + item['tamponi_test_antigenico_rapido']
            italy['yesterday']['positive'] += item['nuovi_positivi']

        if is2DaysAgo:
            italy['yesterday']['test'] += item['tamponi_test_molecolare'] + item['tamponi_test_antigenico_rapido']

        italy['total']['positive'] += item['nuovi_positivi']

    if italy['today']['positive'] == 0:
        time.sleep(60 * 5)
        core()
        return

    italy['today']['healed'] = italy['total']['healed'] - italy['today']['healed']
    italy['today']['death'] = italy['total']['death'] - italy['today']['death']
    italy['today']['hospitalization'] = italy['total']['hospitalization'] - italy['today']['hospitalization']
    italy['today']['severe'] = italy['total']['severe'] - italy['today']['severe']
    print('-----------------------------------------------------------------')
    print(italy['today']['test'], italy['total']['test'])
    italy['yesterday']['test'] = italy['today']['test'] - italy['yesterday']['test']
    italy['today']['test'] = italy['total']['test'] - italy['today']['test']
    print(italy['today']['test'], italy['total']['test'])

    italy['total']['cur'] = italy['total']['positive'] - italy['total']['death'] - italy['total']['healed']
    italy['today']['cur'] = italy['today']['positive'] - italy['today']['death'] - italy['today']['healed']

    lombardi['total']['cur'] = lombardi['total']['positive'] - lombardi['total']['death'] - lombardi['total']['healed']
    lombardi['today']['cur'] = lombardi['today']['positive'] - lombardi['today']['death'] - lombardi['today']['healed']

    #### VACCINE PART
    VACCINE_URL = config['vac_src']
    # sending get request and saving the response as response object
    r = requests.get(url=VACCINE_URL)
    res = r.json()

    vaccinated_numbers = 0
    if res and res['data']:
        for d in res['data']:
            vaccinated_numbers += d['totale']

    print("-------------- italy")
    print(italy)
    print("-------------- lombardia")
    print(lombardi)
    print("--------------")

    text = """
📈 امروز در استان لمباردیا :
({date})

• بیماران کنونی: {current}
({today_current:+})
    
• فوت شدگان: {death}
({today_death:+})

• بهبود یافتگان: {healed}
({today_healed:+})

• مجموع کیسهای کرونا: {positive}
({today_positive:+})

#آمارروزانه
#آمار
🇮🇹 @coronaitaliafarsi
Powered by [Skings](tg://user?id=82768138)
"""

    text = text.format(
        date=datetime.today().utcnow().date().strftime("%d/%m/%Y"),
        current=lombardi['total']['cur'], today_current=lombardi['today']['cur'],
        death=lombardi['total']['death'], today_death=lombardi['today']['death'],
        healed=lombardi['total']['healed'], today_healed=lombardi['today']['healed'],
        positive=lombardi['total']['positive'], today_positive=lombardi['today']['positive'],
        vaccinated_numbers=vaccinated_numbers
    )
    print("--------------")
    print(text)

    data = {
        "chat_id": config['bot']['channel_id'],
        "text": text,
        "parse_mode": "Markdown",
        "disable_notification": config['bot']['silent']
    }
    # requests.post(config['bot']['url'], data)

    text = """
📈 آمار کووید۱۹ مربوط به امروز
🗓   {date}

• مبتلایان امروز: {today_positive:,}
• فوت شدگان امروز: {today_death:,}
• بهبود یافتگان امروز: {today_healed:,}

{today_severe:+,} مراقبهای ویژه | {today_hospitalized:+,} بستری


تعداد تست‌ها {today_test:,}
ضریب جواب مثبت در میان تست‌ها: %{positive_ratio:,.2f} (%{positive_ratio_change:+,.2f})

💉🌸 تعداد دوزهای واکسیناسیون تا به امروز: {vaccinated_numbers:,}

🇮🇹@coronaitaliafarsi

پیش‌بینی ما برای چند روز آینده با توجه به روند آمار در ۷ روز گذشته:
🔗 [Forecast](https://github.com/SamanFekri/ItalyCovid19)

This Bot Powered by [Skings](tg://user?id=82768138) (@SamanFekri)
"""

    text = text.format(
        date=datetime.today().utcnow().date().strftime("%d/%m/%Y"),
        current=italy['total']['cur'], today_current=italy['today']['cur'],
        death=italy['total']['death'], today_death=italy['today']['death'],
        healed=italy['total']['healed'], today_healed=italy['today']['healed'],
        positive=italy['total']['positive'], today_positive=italy['today']['positive'],
        hospitalized=italy['total']['hospitalization'], today_hospitalized=italy['today']['hospitalization'],
        severe=italy['total']['severe'], today_severe=italy['today']['severe'],
        today_test=int(italy['today']['test']),
        positive_ratio=(italy['today']['positive'] / italy['today']['test']) * 100,
        positive_ratio_change=(italy['today']['positive'] / italy['today']['test'] - (italy['yesterday']['positive'] / italy['yesterday']['test'])) * 100,
        vaccinated_numbers=vaccinated_numbers
    )
    print("--------------")
    print(text)
    print("--------------")

    data = {
        "chat_id": config['bot']['channel_id'],
        "text": text,
        "parse_mode": "Markdown",
        "disable_notification": config['bot']['silent'],
        "disable_web_page_preview": True,
    }
    requests.post(config['bot']['url'], data)


try:
    while True:
        x = datetime.today().utcnow()
        print(x)
        publish = {"h": 16, "m": 30}
        if x.today().utcnow().hour < publish['h'] or (
                x.today().utcnow().hour == publish['h'] and x.today().utcnow().minute < publish['m']):
            y = x.replace(day=x.day, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)
        else:
            try:
                y = x.replace(day=x.day + 1, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)
            except ValueError:
                try:
                    y = x.replace(day=1, month=x.month + 1, hour=publish['h'], minute=publish['m'], second=0,
                                  microsecond=0)
                except ValueError:
                    y = x.replace(day=1, month=1, year=x.year + 1, hour=publish['h'], minute=publish['m'], second=0,
                                  microsecond=0)

        delta_t = y - x

        secs = delta_t.seconds + 1

        if config['publish_immediate']:
            core()
        else:
            config['publish_immediate'] = True
        time.sleep(secs)
except KeyboardInterrupt:
    print('Arrivederci')

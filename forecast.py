import requests
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import datetime

from scipy.stats import norm

# api-endpoint
URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json"

# sending get request and saving the response as response object
r = requests.get(url=URL)
res = r.json()

# write data in python
with open('raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=4)

# convert json to dataframe
data = pd.read_json(r'raw_data.json')

data = data.groupby('data')['nuovi_positivi'].sum()
data = data.reset_index(name='nuovi_positivi')
data.index = pd.to_datetime(data['data'], format="%Y-%m-%d")
del data['data']
data.columns = ['nuovi_positivi']


# count, bins, ignored = plt.hist(data['nuovi_positivi'], len(data['nuovi_positivi']), density=True)

# print(count)

## start predict


def x_standard_normal_dist(day, peak_day):
    return 3.0 * ((day / peak_day) - 1.0)


def new_case_at_day(n, last_day_we_have, sum_new_case_we_have, peak_day):
    cdf_n = norm.cdf(x_standard_normal_dist(n, peak_day))
    cdf_n_1 = norm.cdf(x_standard_normal_dist(n - 1, peak_day))

    if n > peak_day:
        d = peak_day + (n - peak_day) / (1.5 - 1 / (n - peak_day))
        cdf_n = norm.cdf(x_standard_normal_dist(d, peak_day))
        cdf_n_1 = norm.cdf(x_standard_normal_dist(d - 1, peak_day))

    pdf_n = cdf_n - cdf_n_1
    ld = x_standard_normal_dist(last_day_we_have, peak_day)

    return (sum_new_case_we_have * pdf_n) / norm.cdf(ld)


# I assume the day == peak_day is max so in standard normal its 0
# I assume the day == 0 is -3 in standard normal
peak = 35.0

until_now = data['nuovi_positivi'].sum()
print("Until now:", until_now)

t = x_standard_normal_dist(len(data['nuovi_positivi']), peak)
expected_case = 1.5 * float(until_now) / norm.cdf(t)
expected_case = int(round(expected_case))
print("Expected total:", expected_case)

predict_more_day = 5
total = len(data['nuovi_positivi']) + predict_more_day
real_data = data['nuovi_positivi'].to_list()
for i in range(predict_more_day):
    real_data.append(0)

predicted_data = []
moving_7_day_sum = 0
trend_direction = 0
trend_limit = {'min': 3.0, 'max': 4.5, 'now': 3.0, 'error': 0.01}
for i in range(total):
    n = new_case_at_day(i, len(data['nuovi_positivi']), until_now, peak)
    sample_from_n_days_ago = 7

    if i < len(data['nuovi_positivi']):
        moving_7_day_sum += real_data[i]
        if i > 0:
            if real_data[i] > real_data[i - 1]:
                trend_direction = min(trend_direction + 0.1, trend_limit['now'])
            else:
                trend_direction = max(trend_direction - 0.1, -trend_limit['now'])

            if real_data[i] > real_data[i - sample_from_n_days_ago]:
                trend_direction = min(trend_direction + 0.8, trend_limit['now'])
            else:
                trend_direction = max(trend_direction - 0.8, -trend_limit['now'])
    else:
        moving_7_day_sum += (1 + trend_direction * 0.1) * real_data[i - sample_from_n_days_ago]

    if i > 7:
        moving_7_day_sum -= real_data[i - 7]

    se = (moving_7_day_sum / 7) / (n + 0.1)
    # if se < 2:
    #     n = (5 * n + 2 * moving_7_day_sum / 7) / 7
    # else:
    if i > 7:
        n = (1 + trend_direction * 0.1) * (3 *(moving_7_day_sum / 7) + 7 * real_data[i - sample_from_n_days_ago]) / 10.0
    else:
        n = (1 + trend_direction * 0.1) * moving_7_day_sum / 7
    n = int(round(n))

    if real_data[i - 1] > 0 and n / real_data[i - 1] > 1.0 + trend_limit['error']:
        trend_limit['now'] = max(trend_limit['now'] - 0.1, trend_limit['min'])
    if n > 0 and real_data[i - 1] / n > 1.0 + trend_limit['error']:
        trend_limit['now'] = min(trend_limit['now'] + 0.1, trend_limit['max'])

    predicted_data.append(n)

dates = [datetime.datetime.utcfromtimestamp(int(posix_time / 1000000000)) for posix_time in data.index.values.tolist()]
for _ in range(predict_more_day):
    dates.append(dates[-1] + datetime.timedelta(days=1))
dates_lbl = [d.strftime("%Y-%m-%d") for d in dates]

## change read me
text = ''
for i in range(predict_more_day):
    text += dates_lbl[-(predict_more_day - i)] + '\t' + '| ' + str(predicted_data[-(predict_more_day - i)]) + '\n'

template = ''
with open('README.tmpl.md', 'r', encoding='utf-8') as f:
    template = f.read()

template = template.replace('{{forecast}}', text)
template = template.replace('{{peak_day}}', dates_lbl[int(peak)])
template = template.replace('{{predict_more_day}}', str(predict_more_day))
template = template.replace('{{until_now}}', str(until_now))
template = template.replace('{{expected_case}}', str(expected_case))

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(template)

y_pos = np.arange(total)
plt.bar(dates_lbl, real_data, align='center')
plt.plot(dates_lbl, predicted_data, 'r')

lbls = [x for x in range(0, len(dates_lbl), 5)]
locs, labels = plt.xticks(ticks=lbls)
plt.setp(labels, rotation=90, fontsize=8)

# locs, labels = plt.yticks(np.arange(0, 6800, step=200))
# plt.setp(labels, fontsize=8)

plt.savefig('forecast.png', bbox_inches='tight')
plt.show()

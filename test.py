import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime

###################################
### First step: update the data ###
###################################


# api-endpoint
URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json"

# sending get request and saving the response as response object
r = requests.get(url=URL)
res = r.json()

# write data in python
with open('raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=4)

# convert json to dataframe
df = pd.read_json(r'raw_data.json')

# write it in csv
df.to_csv('raw_data.csv', sep=',', encoding='utf-8')


###################################
########## Draw Charts ############
###################################

lombardi = df.query("codice_regione == 3")
date = df.groupby('data').median().index.get_level_values('data')
sum_all = df.groupby('data')['nuovi_positivi'].sum()


plt.figure(1)
plt.plot(date, lombardi['nuovi_positivi'], 'r--',
         date, sum_all, 'b--')
locs, labels = plt.xticks()
plt.yticks(np.arange(0, 8000, step=500))
plt.setp(labels, rotation=90, fontsize=8)


plt.figure(2)
ratio = []
i = 0
for item in lombardi['nuovi_positivi']:
    a = float(float(item) / float(sum_all[i]))
    ratio.append(a)
    i += 1
plt.plot(date, ratio)

locs, labels = plt.xticks()
plt.yticks(np.arange(0, 1.1, step=0.1))
plt.setp(labels, rotation=90, fontsize=8)


plt.show()


# print(df)

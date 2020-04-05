import requests
import pandas as pd
import json
import chart_studio.plotly as ply
import cufflinks as cf
import matplotlib.pyplot as plt
import datetime
from statsmodels.sandbox.distributions.mv_normal import mvnormcdf

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
print(data)

data.plot(y='nuovi_positivi', xticks=data.index)

result = mvnormcdf(upper=8000, mu=[8 ], cov=1)


locs, labels = plt.xticks(ticks=data.index)
plt.setp(labels, rotation=90, fontsize=8)
result.plot()

locs, labels = plt.xticks()
plt.setp(labels, rotation=90, fontsize=8)
plt.show()
# ply.iplot(fig)
# print(data)

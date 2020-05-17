import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime

lines = []
lined = dict()
fig, ax = plt.subplots()


def onpick(event):
    # on the pick event, find the orig line corresponding to the
    # legend proxy line, and toggle the visibility
    legline = event.artist
    origline = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)

    fig.canvas.draw()


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
date = [d.split('T')[0] for d in df.groupby('data').median().index.get_level_values('data')]

# we will set up a dict mapping legend line to orig line, and enable
# picking on the legend line
sum_all = df.groupby('data')['nuovi_positivi'].sum()
l, = ax.plot(date, sum_all, label='total')
lines.append(l)

for i in range(1, 23):
    region = df.query("codice_regione == {}".format(i))
    if region.empty:
        continue
    if i == 4:
        new = []
        for j in range(len(region)):
            if j % 2 == 0:
                new.append(region['nuovi_positivi'].iloc[j] + region['nuovi_positivi'].iloc[j + 1])

        l, = ax.plot(date, new,
                     label=region['denominazione_regione'].iloc[0] + '\n&\n' + region['denominazione_regione'].iloc[1])
        lines.append(l)
        continue
    l, = ax.plot(date, region['nuovi_positivi'], label=region['denominazione_regione'].iloc[0])
    lines.append(l)

leg = ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

for legline, origline in zip(leg.get_lines(), lines):
    legline.set_picker(10)  # 5 pts tolerance
    lined[legline] = origline

fig.canvas.mpl_connect('pick_event', onpick)

locs, labels = plt.xticks()
plt.setp(labels, rotation=90, fontsize=8)

plt.savefig('chart.png', bbox_inches='tight')

# plt.show()
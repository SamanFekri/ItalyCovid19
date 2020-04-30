import subprocess as cmd
from datetime import datetime
import time
import json

with open('.env.json') as f:
    config = json.load(f)

print("Config loaded")
print(config)


def core():
    today = datetime.today().date().strftime("%d/%m/%Y")
    cmd.run(f"echo Auto push run the command in '{today}'", check=True, shell=True)

    cp = cmd.run("git pull", check=True, shell=True)

    cp = cmd.run("python3 main.py", check=True, shell=True)
    cp = cmd.run("python3 forecast.py", check=True, shell=True)

    cp = cmd.run("git pull", check=True, shell=True)
    cp = cmd.run("git add .", check=True, shell=True)
    message = "Automatically Update of " + today
    cp = cmd.run(f"git commit -m {message}" , check=True, shell=True)
    cp = cmd.run("git push -u origin master" , check=True, shell=True)

try:
    while True:
        x = datetime.today().utcnow()
        print(x)
        if x.today().utcnow().hour < 16 or (x.today().utcnow().hour == 16 and x.today().utcnow().minute < 30):
            y = x.replace(day=x.day, hour=16, minute=30, second=0, microsecond=0)
        else:
            y = x.replace(day=x.day + 1, hour=16, minute=30, second=0, microsecond=0)
        delta_t = y - x

        secs = delta_t.seconds + 1

        if config['push_immediate']:
            core()
        else:
            config['push_immediate'] = True
        time.sleep(secs)
except KeyboardInterrupt:
    print('Arrivederci')
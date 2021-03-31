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

    cmd.run(f"echo Pulling", check=True, shell=True)
    cmd.run(f"git pull", check=True, shell=True)
    cmd.run(f"echo Pulling finished", check=True, shell=True)
    cmd.run(f"echo ", check=True, shell=True)

    cmd.run(f"echo Run main", check=True, shell=True)
    cmd.run("python3 main.py", check=True, shell=True)
    cmd.run(f"echo main finished", check=True, shell=True)
    cmd.run(f"echo ", check=True, shell=True)

    cmd.run(f"echo run forecast", check=True, shell=True)
    cmd.run("python3 forecast.py", check=True, shell=True)
    cmd.run(f"echo forecast finished", check=True, shell=True)
    cmd.run(f"echo ", check=True, shell=True)

    cmd.run(f"echo add", check=True, shell=True)
    cp = cmd.run("git add .", check=True, shell=True)
    cmd.run(f"echo ", check=True, shell=True)
    print(cp)

    try:
        cmd.run(f"echo commit", check=True, shell=True)
        message = "Automatically Update of " + today
        cmd.run(f"git commit -m '{message}'", check=True, shell=True)
        cmd.run(f"echo ", check=True, shell=True)

        cmd.run(f"echo push", check=True, shell=True)
        cmd.run("git push -u origin master", check=True, shell=True)
        cmd.run(f"echo push ends", check=True, shell=True)
        cmd.run(f"echo ", check=True, shell=True)

    except cmd.CalledProcessError:
        cmd.run(f"echo nothing new", check=True, shell=True)
        cmd.run(f"echo ", check=True, shell=True)


try:
    while True:
        x = datetime.today().utcnow()
        print(x)
        publish = {"h": 16, "m": 45}
        if x.today().utcnow().hour < publish['h'] or (
                x.today().utcnow().hour == publish['h'] and x.today().utcnow().minute < publish['m']):
            y = x.replace(day=x.day, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)
        else:
            try:
                y = x.replace(day=x.day + 1, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)
            except ValueError:
                try:
                    y = x.replace(day=1, month=x.month + 1, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)
                except ValueError:
                    y = x.replace(day=1, month=1, year=x.year + 1, hour=publish['h'], minute=publish['m'], second=0, microsecond=0)

        delta_t = y - x

        secs = delta_t.seconds + 1

        if config['push_immediate']:
            core()
        else:
            config['push_immediate'] = True
        time.sleep(secs)
except KeyboardInterrupt:
    print('Arrivederci')

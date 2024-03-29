import sys
import time

import requests

with open(sys.argv[2], 'r') as file:
    for data in file:
        cool_down = True
        while cool_down:
            resp = requests.get(f'http://localhost:8000/jobs')
            resp_data = resp.json()
            if resp_data['jobs'] < 10:
                print(f'There are {resp_data["jobs"]} jobs currently in progress')
                cool_down = False
            else:
                print(
                    f'COOLING DOWN: sleeping for 5 seconds as there are {resp_data["jobs"]} jobs currently in progress')
                time.sleep(5)
        data = data.strip('\n')
        time.sleep(.2)
        print('>>>', data, '<<<')
        while True:
            try:
                requests.post("http://localhost:8000/wiktionary_page_async/" + sys.argv[1], json={"title": data})
                break
            except KeyboardInterrupt:
                print("Stopped.")
                break
            except requests.exceptions.ConnectionError:
                print("Error... retrying in 10s")
                time.sleep(10)

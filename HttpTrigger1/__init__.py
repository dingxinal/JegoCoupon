import logging

import azure.functions as func
from requests_html import AsyncHTMLSession
import re
from datetime import datetime
import json

invalid_link = [354, 357, 157]
url = 'https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId='

async def main(mytimer: func.TimerRequest, sendGridMessage: func.Out[str]) -> None:
    now = datetime.now()
    cur_date = now.isoweekday()

    asession = AsyncHTMLSession()

    email_value = ""
    count = 0

    range1 = (cur_date - 1) * 100
    range2 = cur_date * 100
    email_value += "遍历" + str(range1) + "至" + str(range2) + "\n"
    for x in range(range1, range2):
        if x in invalid_link:
            continue
        r = await asession.get(url + str(x))
        await r.html.arender(timeout=20)
        html_file = r.html.html

        if "App" not in html_file:
            continue

        try: 
            time = detect_time(html_file)
            if time and (now < time): 
                email_value +=  "Find a new link:" + url + str(x) + "\n"
                count += 1
            elif time is None:
                email_value +=  "A new link cannot find time:" + url + str(x) + "\n"
        except Exception as e:
            logging.critical(e.__doc__)
            email_value +=  "Error happended in" + url + str(x) + ", the reason is" + e.__doc__

        r.close()
        asession.close()
    if count == 0:
        email_value+="毫无发现 \n"

    email_value += """2/3 Update: https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId=354 \n  
        https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId=357"""

    logging.info(email_value)
    message = {
            "personalizations": [{"to": [{"email": "wudingxin1996@gmail.com"}, {"email": "freshqiao@gmail.com"}]}],
            "subject": "[你爹来了Jego] - 我是你爹",
            "content": [{"type": "text/plain", "value": email_value}],
        }
    
    sendGridMessage.set(json.dumps(message))

def detect_time(html_file):
    time = None
    m = re.search("(\d+)年(\d+)月(\d+)日至(\d+)月(\d+)日", html_file)
    if m:
        time = datetime(int(m.groups()[0]), int(m.groups()[3]), int(m.groups()[4]), 0, 0, 0, 0)
        return time

    m1 = re.search("即日起至(\d+)年(\d+)月(\d+)日", html_file)
    if m1:
        time = datetime(int(m1.groups()[0]), int(m1.groups()[1]), int(m1.groups()[2]), 0, 0, 0, 0)
        return time
    
    m2 = re.search("截止时间为(\d+)年(\d+)月(\d+)日", html_file)
    if m2:
        time = datetime(int(m2.groups()[0]), int(m2.groups()[1]), int(m2.groups()[2]), 0, 0, 0, 0)
        return time
    
    m3 = re.search("截止日期为(\d+)年(\d+)月(\d+)日", html_file)
    if m3:
        time = datetime(int(m3.groups()[0]), int(m3.groups()[1]), int(m3.groups()[2]), 0, 0, 0, 0)
        return time
    
    m4 = re.search("截止至(\d+)年(\d+)月(\d+)日", html_file)
    if m4:
        time = datetime(int(m4.groups()[0]), int(m4.groups()[1]), int(m4.groups()[2]), 0, 0, 0, 0)
        return time
    return time
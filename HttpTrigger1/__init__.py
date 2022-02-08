import logging

import azure.functions as func
from requests_html import AsyncHTMLSession
import re
from datetime import datetime
import json

async def main(mytimer: func.TimerRequest, sendGridMessage: func.Out[str]) -> None:
    logging.info('Python HTTP trigger function processed a request.')
    asession = AsyncHTMLSession()

    url = 'https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId='
    email_value = ""
    count = 0
    now = datetime.now()
    cur_date = now.isoweekday()

    range1 = cur_date * 100
    range2 = (cur_date + 1) * 100
    email_value+= "遍历" + str(range1) + "至" + str(range2) + "\n"
    for x in range(range1, range2):
        if x == 354 or x == 357:
            continue
        r = await asession.get(url + str(x))
        await r.html.arender(timeout=20)
        html_file = r.html.html
        text = ""
        if "App" in html_file:
            if "活动时间" in html_file: 
                try:
                    m = re.search("(\d+)年(\d+)月(\d+)日至(\d+)月(\d+)日", html_file)
                    t = datetime(int(m.groups()[0]), int(m.groups()[3]), int(m.groups()[4]), 0, 0, 0, 0) if m else None

                    m1 = re.search("至(\d+)年(\d+)月(\d+)日", html_file)
                    t1 = datetime(int(m1.groups()[0]), int(m1.groups()[1]), int(m1.groups()[2]), 0, 0, 0, 0) if m1 else None
                    if m and t and (now < t): 
                        text = "Find a new link:" + url + str(x) + "\n"
                        count+1
                    elif m1 and t1 and (now < t1):
                        text = "Find a new link:" + url + str(x) + "\n"
                        count+1
                    elif t1 is None and t is None:
                        text = "A new link cannot find time:" + url + str(x) + "\n"
                except Exception as e:
                    logging.critical(e.__doc__)
                    text = "Error happended in" + url + str(x) + ", the reason is" + e.__doc__
            else:
                text = "A new link with no time specifed:" + url + str(x) + "\n"
            email_value+=text
        r.close()
        asession.close()
    if count == 0:
        email_value+="毫无发现 \n"
        email_value+="------------------------------------------- \n"
        email_value+="2/3 Update: https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId=354 \n  https://cp.jegotrip.com.cn/partners/skuact/index.html?actName=act1&actId=357"
    logging.info(email_value)
    message = {
            "personalizations": [{"to": [{"email": "wudingxin1996@gmail.com"}, {"email": "freshqiao@gmail.com"}]}],
            "subject": "[你爹来了Jego] - 我是你爹",
            "content": [{"type": "text/plain", "value": email_value}],
        }
    
    sendGridMessage.set(json.dumps(message))
import os
import requests

cookies = {
    # 'JSESSIONID': '95D976E3EE9DCF50BC129BA4FAFCAAFC',
    # 'user': '2|1:0|10:1582511687|4:user|16:MTAwMTA0OTYzNw==|ec39735b75c4ce0a1ca234fc4b0ba9038cc196f5b654f76f12a43427c29935a9',
    # 'ngxid': 'rBFdFF5TNjpOWx2OCnvqAg==',
}

auth = os.getenv("TIGER_API_AUTHORIZATION")
params = (("startDate", "2000-01-01"), ("endDate", "2050-01-01"))


def get_ipo_calendar():
    headers = {
        'User-Agent': 'Stock/6.7.4 (iPhone; iOS 13.3.1; Scale/3.00)',
        'Host': 'hq1.itiger.com',
        'Authorization': auth,
        'X-API-Version': 'v2',
    }
    response = requests.get(
        'https://hq1.itiger.com/calendar/ipo',
        headers=headers,
        params=params,
        cookies=cookies,
        verify=False,
    )
    data = response.json()
    if data.get('error'):
        post_me('now.calendars 的老虎证券的 Authorization 过期了')
    return response


def post_me(text):
    if not text:
        return
    url = "https://hub.drink.cafe/http"

    res = requests.post(
        url,
        json={
            "action": "PUB",
            "topics": ["weaming"],
            "message": {"type": "PLAIN", "data": text},
        },
    )
    if res.status_code == 200:
        return res.text
    else:
        raise Exception("Unexpected response code {}".format(res.status_code))

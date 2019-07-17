import os
import requests

cookies = {
    # "JSESSIONID": "69ADCC7335E61DB528E078558424542A",
    # "user": "2|1:0|10:1563363750|4:user|16:MTAwMTA0OTYzNw==|b5da20af67e3dcf4aa9fca186cb5a0311f5462ba07b79d2890803f3603411bf8",
    # "aliyungf_tc": "AQAAALloHifcdwcAF490cah6m4dQAbVi",
    # "ngxid": "fPoiPl0u1dOfb4Ig1LXhAg==",
}

headers = {
    "User-Agent": "Stock/6.6.2 (iPhone; iOS 12.3.2; Scale/3.00)",
    "Host": "hq2.itiger.com",
    "Authorization": os.getenv("TIGER_API_AUTHORIZATION"),
    # "X-API-Version": "v2",
    # "X-NewRelic-ID": "XAUGVl9TGwYCXVFaBAk=",
}

params = (
    ("startDate", "2018-01-01"),
    ("endDate", "2100-01-01"),
    # ("device", "iPhone 8 Plus"),
    # ("deviceId", "603b8acfb9e2a38c7be6a56fb9416ff09f5edba1"),
    # ("appVer", "6.6.0.2"),
    # ("vendor", "AppStore"),
    # ("platform", "iOS"),
    # ("channel", "AppStore"),
    # ("lang", "zh_CN"),
    # ("screenW", "414"),
    # ("keyfrom", "TigerBrokers.6.6.0.2.iPhone"),
    # ("screenH", "736"),
    # ("osVer", "12.3.2"),
)


def get_ipo_calendar():
    response = requests.get(
        "https://hq2.itiger.com/calendar/ipo",
        headers=headers,
        params=params,
        cookies=cookies,
        verify=False,
    )
    return response

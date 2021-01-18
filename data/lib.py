import requests
from bs4 import BeautifulSoup
from bs4.element import Comment


UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'


def get_url_text(url, json=False, params=None, encoding='utf8', allow_redirects=True):
    res = requests.get(
        url,
        params=params,
        headers={'User-Agent': UA},
        allow_redirects=allow_redirects,
    )
    res.encoding = encoding
    if res.status_code == 200:
        if json:
            return res.json()
        return res.text
    elif res.status_code in [301, 302]:
        return res.headers.get('location')
    else:
        raise Exception("Unexpected response code {}".format(res.status_code))


def url2soup(url, params=None, encoding='utf8'):
    html = get_url_text(url, params=params, json=False, encoding=encoding)
    return html2soup(html)


def html2soup(html):
    return BeautifulSoup(html, "html.parser")

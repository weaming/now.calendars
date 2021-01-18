from .lib import url2soup


def get_all_ipo_data():
    data = None
    for i in range(100):
        page = ipo_single_page(i)
        if page is None or i >= 5:
            return data
        data = (data + page) if data is not None else page


def ipo_single_page(n=1):
    s = url2soup(
        f'https://vip.stock.finance.sina.com.cn/corp/view/vRPD_NewStockIssue.php?page={n}&cngem=0&orderBy=NetDate&orderType=desc',
        encoding='gb2312',
    )
    rows = s.select('#NewStockTable tr')[2:]
    if not rows:
        return None
    header = [x.text.strip(' ↓') for x in rows[0].select('td')]
    data = [
        dict(zip(header[:-3], [xx.text.strip() for xx in x.select('td')[:-3]]))
        for x in rows[1:]
    ]
    return data
    # import pandas as pd
    # data = pd.DataFrame(data)
    # return data


# print(ipo_single_page(8))
# print(get_all_ipo_data().to_dict('records'))
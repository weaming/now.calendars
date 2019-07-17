import os

from .common import http_get_url, prepare_dir, get_root_dir
from .ics_patch import *


def get_ipo_list(api):
    err, data = http_get_url(api, is_json=True)
    if err:
        raise Exception(f"error: {err}; data: {data}")
    return [x for x in data["rawData"]]


def get_ics_output():
    ics_output = os.path.expanduser(
        os.getenv("ICS_OUTPUT")
        or os.path.join(get_root_dir(), "output/upcomming-ipos.ics")
    )
    return ics_output


def update_ics(data, cal_name="Upcommming IPOs"):
    ics_output = get_ics_output()
    prepare_dir(ics_output)

    if os.path.isfile(ics_output):
        container = string_to_container(open(ics_output).read())
        events = [x for x in container[0] if x.name == "VEVENT"]
    else:
        events = None

    c = Calendar(events=events)
    for x in data:
        desc = f"market: {x['market']}, address: {x['address']}, status: {x['status']}, employees: {x['employees']}, revenue: {x['revenue']}"
        begin = f"{x['expectedDate']}T08:00:00-04:00"
        e = Event(
            uid=x["symbol"],
            name=f"{x['symbol']} | {x['companyName'].strip()}",
            begin=begin,
            # duration=datetime.timedelta(hours=12),
            description=desc,
            transparent=True,
            url=x["url"],
            # status={
            #     'FILLED': 'CONFIRMED',
            #     'CANCELLED': 'CANCELLED',
            # }.get(x['status'], 'TENTATIVE'),
            categories=["stock", "financial"],
            alarms=[DisplayAlarm(trigger=get_arrow(begin))],
        )

        # remove by hash
        if e in c.events:
            c.events.remove(e)

        # add the newer one
        c.events.add(e)

    # print(c.events)
    with open(ics_output, "w") as f:
        wrote = False
        for l in c:
            f.write(l)
            if not wrote and l.startswith("VERSION"):
                f.write(f"X-WR-CALNAME:{cal_name}\n")
                wrote = True

    print(f"wrote {ics_output}")


def gen_ics():
    token = os.getenv("IEX_APIS_TOKEN")
    api = f"https://cloud.iexapis.com/stable/stock/market/upcoming-ipos?token={token}"
    data = get_ipo_list(api)
    update_ics(data)

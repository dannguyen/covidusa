from colorama import init as colorinit, Back as cBack, Fore as cFore
from colorama import Style as cStyle
from datetime import date, timedelta
import pdb
import requests
from sys import stdout, stderr

colorinit(autoreset=True)

def loggy(txt, process_name=None, level=1):
    if process_name:
        prefix =f"{cBack.BLACK + cFore.YELLOW + cStyle.BRIGHT + process_name}:{cStyle.RESET_ALL}"
        msg = f'{prefix} {txt}'
    else:
        msg = txt

    stderr.write(f"{msg}\n")


def daysdiff(dy, dx):
    return (date.fromisoformat(dy) - date.fromisoformat(dx)).days

def date_daysahead(dt, days):
    """ dt(str): '2019-02-10'
        days(int): 3

        Returns: (str) '2019-02-14'"""
    return (date.fromisoformat(dt) + timedelta(days=days)).isoformat()


def days_between(dx, dy):
    diff = daysdiff(dy, dx)
    if diff < 2:
        return [] # no days between consecutive days
    else:
        return [date_daysahead(dx, i) for i in range(1, diff)]


def fetch_and_save(url, dest_path):
    resp = requests.get(url)
    if resp.status_code == 200:
        loggy(f"Downloaded {len(resp.content)} bytes from: {url}")
        with open(dest_path, 'wb') as outs:
            loggy(f"\tWrote {len(resp.content)} bytes to: {dest_path}")
            outs.write(resp.content)
    else:
        emsg = f"Got unexpected status code of: {resp.status_code} from {url}"
        loggy(emsg)
        pdb.set_trace()
        raise ValueError(emsg)




# def idebug(thevars, error=None):
#     import pdb; pdb.set_trace() # inject for fun
#     if error:
#         raise error

#!/usr/bin/python3

import requests
from time import sleep
import pickle

try:
    region_id = sys.argv[1]
    if not len(region_id):
        raise
except:
    region_id = 10000002

fn = 'market_orders.pickle'

try:
    data = None
    data = pickle.load(open(fn,'rb'))
except:
    pass

if data is not None:
    print("Loaded {:,} previously fetched market orders.".format(len(data)))
    sleep(1)

else: # not loaded, start fresh
    url = 'https://esi.evetech.net/latest/markets/{}/orders/?datasource=tranquility&order_type=all&page='.format(region_id)
    r = requests.get('{}1'.format(url))
    last_page = int(r.headers['X-Pages']) # last page number in header

    print("Fetching all {} pages of the market data for region_id {}.".format(last_page, region_id))
    sleep(3)

    for page in range(1, last_page+1):
        theurl = '{}{}'.format(url, page)
        print(theurl)

        count = 5
        while count > 0:
            try:
                count -= 1
                r = requests.get(theurl)
                if r.status_code == 200:
                    for d in r.json():
                        data.append(d)
                    break
            except Exception as e:
                print(e)
                sleep(5)
                print("RETRYING",theurl)

        sleep(5.5)

        with open(fn, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


with open('items.txt', 'r') as f:
    items = eval(f.read())

buys = {}
sells = {}
for d in data:
    #print(d.keys())
    # keys: ['duration', 'is_buy_order', 'issued', 'location_id', 'min_volume', 'order_id', 'price', 'range', 'system_id', 'type_id', 'volume_remain', 'volume_total']

    try:
        d['name'] = items.get(d['type_id'], 'Unknown')
    except Exception as e:
        print(d)
        print(type(d))
        print(e)
        import sys
        sys.exit(1)

    if d['is_buy_order']:
        try:
            buys[d['type_id']].append(d)
        except KeyError:
            buys[d['type_id']] = [d]

    else: # sell order
        try:
            sells[d['type_id']].append(d)
        except KeyError:
            sells[d['type_id']] = [d]

with open('market_buys.pickle', 'wb') as f:
        pickle.dump(buys, f, protocol=pickle.HIGHEST_PROTOCOL)
with open('market_sells.pickle', 'wb') as f:
        pickle.dump(sells, f, protocol=pickle.HIGHEST_PROTOCOL)


import requests
# from xml.dom import minidom
import xml.etree.ElementTree as ET
import json
import csv


SOURCE_ITEM_DB = 'item_db.csv'
SOURCE_ITEM_DB_FIELDS = ['item_name', 'boss', 'type']

TARGET_ITEM_DB = 'item_stats_db.csv'

items = []
stat_types = {}
stat_ignore = {
    "appearances": True,
    "agiint": True,
    "agistr": True,
    "classes": True,
    "cooldown": True,
    "displayid": True,
    "dmgrange": True,
    "dmgtype1": True,
    "dps": True,
    "dura": True,
    "maxcount": True,
    "mledmgmax": True,
    "mledmgmin": True,
    "mledps": True,
    "mlespeed": True,
    "reqlevel": True,
    "sellprice": True,
    "shares": True,
    "sheathtype": True,
    "slotbak": True,
    "strint": True,
    "versatility": True,
}


def wowhead_url(item_name):
    return 'https://classic.wowhead.com/item={}&xml'.format(item_name)


def fetch_items(item_name):
    fetched_items = []

    url = wowhead_url(item_name)
    r = requests.get(url)
    item_tree = ET.fromstring(r.text)

    for item in item_tree.iter('wowhead'):
        fetched_items.append(parse_item(item))

    return fetched_items


def parse_item(item):
    item_stats = json.loads('{' + item.findtext('item/jsonEquip') + '}')
    item_data = dict(filter(lambda elem: elem[0] not in stat_ignore, item_stats.items()))
    for key in item_data.keys():
        stat_types[key] = True

    item_data['id'] = item.find('item').attrib.get('id')

    name = item.findtext('item/name')
    url = item.findtext('item/link')
    item_data['name'] = '=HYPERLINK("{}";"{}")'.format(url, name)

    return item_data


def item_row(item):
    item = [
        item.name,
        item.id,
    ]
    for stat_name in stat_types.keys():
        item.append(item.stats.get(stat_name, ''))
    return item


def get_source_items():
    source_item_names = []

    with open(SOURCE_ITEM_DB) as source_file:
        reader = csv.DictReader(
            filter(lambda row: row[0] != '#', source_file),
            dialect=csv.excel_tab,
            fieldnames=SOURCE_ITEM_DB_FIELDS)
        for row in reader:
            source_item_names.append(row['item_name'])
    
    return source_item_names


def print_db():
    source_item_names = get_source_items()

    print('Fetching items...')
    for item_name in source_item_names:
        print('- {}'.format(item_name))
        for item in fetch_items(item_name):
            items.append(item)

    with open(TARGET_ITEM_DB, mode='w', newline='') as target_file:
        header = list(stat_types.keys())
        header.sort()
        header.insert(0, 'id')
        header.insert(0, 'name')
        writer = csv.DictWriter(
            target_file,
            delimiter='\t',
            # dialect=csv.excel_tab,
            fieldnames=header,
        )
        writer.writeheader()

        for item in items:
            writer.writerow(item)



if __name__ == '__main__':
    # fetch_item('Benediction')
    # print(json.dumps(stat_types, indent=2))
    print_db()

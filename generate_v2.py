#!/usr/bin/env python3

import argparse
import csv
import requests
import re
from lxml import html
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--user", help="Github Username to get activity for", required=True)
parser.add_argument("--year", help="Year for activity to be generated for", required=True)
parser.add_argument("--markup", help="Manually input markup incase the page is private", required=False)
args = parser.parse_args()

start_date = datetime(int(args.year), 1, 1)
#end_date = datetime(int(args.year) + 1, 1, 1) - timedelta(days=1)
day_offset = start_date.weekday() + 1

if args.markup:
    tree = html.fromstring(args.markup)
else:
    page = requests.get(f'https://github.com/{args.user}?tab=overview&from={args.year}-01-01&to={args.year}-12-31')
    tree = html.fromstring(page.content)

rawDays = tree.xpath('//svg[@class="js-calendar-graph-svg"]//rect[@class="ContributionCalendar-day"]')

days = []

for rawDay in rawDays:
    match = re.search("^\d+", rawDay.text_content())
    if match == None:
      contributionCount = 0
    else:
      contributionCount = int(match.group())

    days.append(contributionCount)

print(days)

maxiumum_height_mm = 25
most_contributions = max(days)
percent_height_per_contribution = (100 / most_contributions) / 100
height_per_contribution_mm = maxiumum_height_mm * percent_height_per_contribution

filename = args.user + "_" + args.year + ".csv"

with open(filename, 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(["maxheight", "mm", str(maxiumum_height_mm) + " mm"])

    index = 0

    for i in range(0, day_offset):
        index += 1
        writer.writerow(["day" + str(index), "mm", str(maxiumum_height_mm) + " mm"])

    for day in days:
        index += 1
        height_adjustment = day * height_per_contribution_mm
        writer.writerow(["day" + str(index), "mm", str(maxiumum_height_mm - height_adjustment) + " mm", day])

print("total contributions: " + str(sum(days)))
print("output " + filename)

#!/usr/bin/env python3

import argparse
import csv
import requests
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--user", help="Github Username to get activity for", required=True)
parser.add_argument("--key", help="Your Github API key", required=True)
parser.add_argument("--year", help="Year for activity to be generated for", required=True)
args = parser.parse_args()

start_date = datetime(int(args.year), 1, 1)
end_date = datetime(int(args.year) + 1, 1, 1) - timedelta(days=1)
day_offset = start_date.weekday() + 1

headers = {"Authorization": "Bearer " + args.key}
query = f"""
{{
  user(login: \"{args.user}\") {{
    contributionsCollection(from: \"{start_date.isoformat()}\", to: \"{end_date.isoformat()}\") {{
      commitContributionsByRepository {{
        contributions(first: 5) {{
          totalCount
          nodes {{
            commitCount
            occurredAt
          }}
        }}
      }}
      restrictedContributionsCount
      contributionCalendar {{
        totalContributions
        weeks {{
          contributionDays {{
            contributionCount
            date
          }}
        }}
      }}
    }}
  }}
}}
"""

request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
if request.status_code == 200:
    result = request.json()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

print(result)

if int(result["data"]["user"]["contributionsCollection"]["restrictedContributionsCount"]) > 0:
    print("There is some hidden activity: " + str(result["data"]["user"]["contributionsCollection"]["restrictedContributionsCount"]))

weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = []

for week in weeks:
    days.extend(week["contributionDays"])

maxiumum_height_mm = 25
most_contributions_day = max(days, key=lambda d: d["contributionCount"])
percent_height_per_contribution = (100 / int(most_contributions_day["contributionCount"])) / 100
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
        height_adjustment = int(day["contributionCount"]) * height_per_contribution_mm
        writer.writerow(["day" + str(index), "mm", str(maxiumum_height_mm - height_adjustment) + " mm", day["date"], day["contributionCount"]])

print("total contributions: " + str(result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]))
print("output " + filename)

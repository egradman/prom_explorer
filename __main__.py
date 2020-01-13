"""

Fetch and analyze the unique metrics in a prometheus instance.

Run `python3 . fetch` to download a JSON file containing the labels for each unique series
Run `analyze` to count the entries in each file

"""
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import os
import glob
from operator import itemgetter
import click

from dotenv import load_dotenv
load_dotenv()

# set these in a .env file
auth=HTTPBasicAuth(
  os.getenv("USERNAME"),
  os.getenv("PASSWORD")
)

@click.group()
def cli():
  pass

@cli.command()
def fetch():
  """create a JSON file containing the unique labels for each series"""

  # get all the series names
  url = 'https://prometheus-us-central1.grafana.net/api/prom/api/v1/label/__name__/values'
  all_series = requests.get(url, auth=auth).json()["data"]

  try:
    os.mkdir("data")
  except FileExistsError:
    pass

  # for each series, get all the labels
  url = 'https://prometheus-us-central1.grafana.net/api/prom/api/v1/series'
  for series in all_series:
    data = requests.get(url, {
      "match[]": series
    }, auth=auth).json()

    with open(f"data/{series}.json", "w") as f:
      json.dump(data, f)

@cli.command()
def analyze():
  series_counts = {}
  for filename in glob.glob("data/*.json"):
    series_name = re.match(r"data/(.+)\.json", filename).group(1)

    data = json.load(open(filename))["data"]

    series_counts[series_name] = len(data)
  
  for series_name, count in sorted(series_counts.items(), key=itemgetter(1)):
    print(f"{count}\t{series_name}")

  total = sum(series_counts.values())
  print(f"total: {total}")

if __name__=='__main__':
  cli()

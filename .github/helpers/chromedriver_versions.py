import argparse
from urllib import request
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-fv', '--full-version', type=str,
                    help="The full version number of the run's Chromium app")
# parser.add_argument('-mv', '--major-version', type=str,
#                     help="The major version number of the run's Chromium app")
args = parser.parse_args()

# Fetch the chromedriver downloads page to see which versions are available
url = 'https://chromedriver.chromium.org/downloads'
req = request.urlopen(url)
if req.status >= 400:
    raise RuntimeError(f"HTTP response was {req.status}; job derailed.")
soup = BeautifulSoup(req.read(), 'html.parser')

# filter the page down to lists of full and major versions available
ver_str = soup.select('a.XqQF9c > strong')
if len(ver_str) == 0:
    raise ValueError("No matching tags on Chromedriver downloads page. "
                     "Action author should re-check references. Job derailed.")
versions = [v.text.split()[1] for v in ver_str]
versions_maj = [vv.split('.')[0] for vv in versions]
major_version = args.full_version.split('.')[0]

if args.full_version in versions:
    print(args.full_version)
elif major_version in versions_maj:
    print(next(v for v in versions if v.startswith(major_version)))
else:
    raise ValueError("Discrepancy between default Ubuntu Chromium "
                     f"(v{args.full_version}) and versions listed on "
                     "chromedriver download page. Job derailed.")

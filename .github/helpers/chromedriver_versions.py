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
req = request.urlopen(url).read()
soup = BeautifulSoup(req, 'html.parser')
# need to address case when there's a 404 or the page looks different than expected...

# filter the page down to lists of full and major versions available
ver_str = soup.select('a.XqQF9c > strong')
versions = [v.text.split()[1] for v in ver_str]
versions_maj = [vv.split('.')[0] for vv in versions]
major_version = args.full_version.split('.')[0]

if args.full_version in versions:
    print(args.full_version)
elif major_version in versions_maj:
    print(next(v for v in versions if v.startswith(major_version)))
# need an else case for unexpected outcomes...

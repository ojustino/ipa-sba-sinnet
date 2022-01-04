import argparse
from urllib import request
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-fv', '--full-version', type=str,
                    help="The full version number of the run's Chromium app")
# parser.add_argument('-mv', '--major-version', type=str,
#                     help="The major version number of the run's Chromium app")
args = parser.parse_args()

# Find all open pull requests with automation tag
url_root = 'https://github.com'
url_rest = '/ojustino/tennis-abs-api/pulls?q=is%3Apr+is%3Aopen+label%3Atest'
req = request.urlopen(url_root + url_rest).read()
soup = BeautifulSoup(req, 'html.parser')
# need to address case when there's a 404 or the page looks different than expected...

# Get links to those pull requests
matching_tags = soup.select('div.flex-auto.min-width-0 > a')
matching_pages = [a.get('href') for a in matching_tags]

# If they exist, read webpages one by one
proceed = 'yes'
for rest in matching_pages:
    _req = request.urlopen(url_root + rest).read()
    _soup = BeautifulSoup(_req, 'html.parser')
    # need to address case when there's a 404 or the page looks different than expected...

    title = _soup.select('span.js-issue-title.markdown-title')[0]
    intro = _soup.select('td.comment-body > p')[0]

    # if title or body text don't match expected format, move on
    if title.text.split()[0] != '[AUTO]' or 'Moved' not in intro.text:
        continue

    pr_cd_ver = intro.text.split()[-1][:-1]

    # only proceed if the PR's chromedriver version is not the same
    if 'v' + args.full_version == pr_cd_ver:
        proceed = ''
    else:
        continue
    # what if args.full_version.split('.')[0] > pr_cd_ver.split('.')[0]?

print(proceed)

# what about checking out the existing branch with the highest chromedriver
# version and pushing there instead of opening a new PR? or adding
# "closes #X" to the bot's PR body for each existing PR with a lower version?

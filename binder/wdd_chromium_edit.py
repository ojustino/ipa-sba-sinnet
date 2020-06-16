# The webdriverdownloader (wdd) and webdriver_manager (wd_m) packages offer
# methods of downloading the chromedriver file needed to use Chrome with
# selenium, but I've run into problems with the Chrome webdriver that don't
# happen with Firefox's. In this file, I attempt to blend wb_m's Chrome version
# checking code with wdd's code for downloading and installing chromedriver. I
# also hope to shift the browser being searched for on the machine from Chrome
# to Chromium. (File was created after webdriver_chromium_edit didn't work.)

import logging
import os
import platform
import requests
import re

from bs4 import BeautifulSoup
from webdriverdownloader import ChromeDriverDownloader
from webdriverdownloader.util import get_architecture_bitness
from webdriver_manager.utils import OSType, os_name

logger = logging.getLogger(__name__)

# this is from wb_m
def chromium_version(browser_type='chromium'):
    pattern = r'(\d+\.?)+' # generalized the regex a bit

    cmd_mapping = {
        'chromium': {
            OSType.LINUX: 'chromium --version || chromium-browser --version',
            OSType.MAC: r'/Applications/Chromium.app/Contents/MacOS/Chromium --version',
            OSType.WIN: r'reg query "HKEY_CURRENT_USER\Software\Chromium\BLBeacon" /v version'
        }
    }

    cmd = cmd_mapping[browser_type][os_name()]
    stdout = os.popen(cmd).read()
    version = re.search(pattern, stdout)
    if not version:
        raise ValueError(f'Could not get version for Chrome with this command: {cmd}')
    current_version = version.group(0)
    return current_version # something like "81.0.4044.138" or "83.0.4103.61"

# next, re-write methods in ChromeDriverDownloader (and its parent,
# WebDriverDownloaderBase, which we can't import due to wdd's __init__.py)
# that control how the drivers are downloaded to act more like wd_m and leave
# the file writing and symlinking to wdd, since that part seems to work for FF
def check_download_version(version, os_name, bitness):
    # a function of my own to ensure there's a matching driver for the
    # current OS' chromium verison
    major_vers = r"\d+" # first instance of numbers only
    os_bit = f"{os_name}{bitness}"

    resp = requests.get("http://chromedriver.storage.googleapis.com/")
    soup = BeautifulSoup(resp.content.decode(), features='xml')
    major_matches = [key.text for key in soup.find_all("Key")
                     if re.match(major_vers, key.text)
                     and re.search(os_bit, key.text)]
    exact_match = [txt for txt in major_matches
                   if re.match(r'(\d+\.?)+', txt).group() == version]

    if exact_match:
        print('exact chromedriver match')
        return exact_match.pop()
    elif major_matches:
        print('matched chromedriver major version')
        return major_matches[0] # earlier so driver isn't newer than OS version?
    else:
        raise ValueError(f"No matching chromedriver for version {major_vers}."
                         "Try antoher Chromium version or a different browser.")

def get_download_url(self, version="latest", os_name=None, bitness=None):
    """
    Method for getting the download URL for the Google Chome driver binary.

    :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                    Default if no version is specified is "latest".  The version string should match the version
                    as specified on the download page of the webdriver binary.
    :param os_name: Name of the OS to download the web driver binary for, as a str.  If not specified, we will use
                    platform.system() to get the OS.
    :param bitness: Bitness of the web driver binary to download, as a str e.g. "32", "64".  If not specified, we
                    will try to guess the bitness by using util.get_architecture_bitness().
    :returns: The download URL for the Google Chrome driver binary.
    """
    # if version == "latest":
    #     version = self._get_latest_version_number()
    version = chromium_version()
    print(version)

    if os_name is None:
        os_name = platform.system()
        if os_name == "Darwin":
            os_name = "mac"
        elif os_name == "Windows":
            os_name = "win"
        elif os_name == "Linux":
            os_name = "linux"
    if bitness is None:
        bitness = get_architecture_bitness()
        logger.debug("Detected OS: {0}bit {1}".format(bitness, os_name))

    # check if drivers for the correct Chromium major version are present
    rest_url = check_download_version(version, os_name, bitness)

    # at this point, we have base_url, version, OS, and bitness, which should
    # be enough to generate a URL
    #filename = f"{self.get_driver_filename()}_{os_name}{bitness}.zip"
    #download_url = os.path.join(self.chrome_driver_base_url, version, filename)
    filename = os.path.split(rest_url)[-1]
    download_url = os.path.join(self.chrome_driver_base_url, rest_url)

    # chrome_driver_objects = requests.get(self.chrome_driver_base_url + '/o')
    # matching_versions = [item for item in chrome_driver_objects.json()['items'] if item['name'].startswith(version)]
    # os_matching_versions = [item for item in matching_versions if os_name in item['name']]
    # if not os_matching_versions:
    #     error_message = "Error, unable to find appropriate download for {0}.".format(os_name + bitness)
    #     logger.error(error_message)
    #     raise RuntimeError(error_message)
    # elif len(os_matching_versions) == 1:
    #     result = os_matching_versions[0]['mediaLink']
    # elif len(os_matching_versions) == 2:
    #     result = [item for item in matching_versions if os_name + bitness in item['name']][0]['mediaLink']

    return download_url # this is passed to WebDriverDownloaderBase.download()

def get_download_path(self, version="latest"):
    # if version == "latest":
    #     ver = self._get_latest_version_number()
    # else:
    #     ver = version
    return os.path.join(self.download_root, "chrome", chromium_version())

# need to change download() as well

ChromiumDriverDownloader = ChromeDriverDownloader
ChromiumDriverDownloader.get_download_url = get_download_url
ChromiumDriverDownloader.get_download_path = get_download_path
ChromiumDriverDownloader.chrome_driver_base_url = 'http://chromedriver.storage.googleapis.com'

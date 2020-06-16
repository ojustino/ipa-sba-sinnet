# The webdriverdownloader (wdd) and webdriver_manager (wd_m) packages offer
# methods of downloading the chromedriver file needed to use Chrome with
# selenium, but I've run into problems with the Chrome webdriver that don't
# happen with Firefox's. In this file, I attempt to blend wd_m's chromedriver
# downloading and installation code with wdd's symlinking code to help put
# Chromedriver in the correct directory. I also hope to shift the browser being
# searched for on the machine from Chrome to Chromium.

import logging
import os
import re
import requests
import stat

from webdriver_manager import utils
from webdriver_manager.driver import Driver
from webdriver_manager.logger import log
from webdriver_manager.manager import DriverManager
from webdriver_manager.utils import OSType, os_name, validate_response

def chromium_version(browser_type='chromium'):
    pattern = r'\d+\.\d+\.\d+'

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
    return current_version

class ChromiumDriver(Driver):
    def __init__(self, name, version, os_type, url, latest_release_url,
                 chrome_type='chromium'):#chrome_type=ChromeType.GOOGLE):
        super(ChromiumDriver, self).__init__(name, version, os_type, url,
                                           latest_release_url)
        self.chrome_type = chrome_type
        self.browser_version = chromium_version(chrome_type)

    def get_os_type(self):
        if "win" in super().get_os_type():
            return "win32"
        return super().get_os_type()

    def get_latest_release_version(self):
        log(f"Get LATEST driver version for {self.browser_version}")
        resp = requests.get(f"{self._latest_release_url}_{self.browser_version}")
        validate_response(resp)
        return resp.text.rstrip()

class ChromiumDriverManager(DriverManager):
    def __init__(self, version="latest",
                 os_type=utils.os_type(),
                 path=None,
                 name="chromedriver",
                 url="http://chromedriver.storage.googleapis.com",
                 latest_release_url="http://chromedriver.storage.googleapis.com/LATEST_RELEASE",
                 chrome_type='chromium',#chrome_type=ChromeType.GOOGLE,
                 log_level=logging.INFO):
        super().__init__(path, log_level=log_level)

        self.driver = ChromiumDriver(name=name,
                                     version=version,
                                     os_type=os_type,
                                     url=url,
                                     latest_release_url=latest_release_url,
                                     chrome_type=chrome_type)

        # from wdd
        if os_type in {'linux64', 'linux32', 'mac64', 'mac32'}:# and os.geteuid() == 0:
            # THIS IS NOT WORKING PROPERLY.... geteuid is not 0 in Docker build
            base_path = "/usr/local"
        else:
            base_path = os.path.expanduser("~")

        # wdd uses a different download directory
        # if os_type in {OSType.LINUX, OSType.MAC}:
        #     self.download_root = os.path.join(base_path, "webdriver")
        # else:
        #     self.download_root = os.path.join(os.environ['HOME'], "webdriver")

        if os_type in {'linux64', 'linux32', 'mac64', 'mac32'}:
            self.link_path = os.path.join(base_path, "bin")
        else:
            self.link_path = os.path.join(os.environ['HOME'], "bin")

        # if not os.path.isdir(self.download_root):
        #     os.makedirs(self.download_root)
        #     logger.info("Created download root directory: {0}".format(self.download_root))
        if not os.path.isdir(self.link_path):
            os.makedirs(self.link_path)
            log("Created symlink directory: {0}".format(self.link_path))

    def install(self):
        # chrome_type comes from this class' __init__ argument
        # browser_version comes from ChromiumDriver's __init__, which calls my
        # edited chromium_version() method.
        log(f"Current {self.driver.chrome_type} version is {self.driver.browser_version}", first_line=True)
        # calls a DriverManager method that gets browser_version (e.g. 81.*,
        # 83.*, like above), driver_name, os_type, and driver_version (probably
        # "latest") from Driver. These are used to call DriverCache's
        # find_driver() method, which collects metadata from that class'
        # get_metadata() method to check if there's an existing driver in wdm's
        # cache and skip a download if so. if not, _get_driver_path continues on
        # to utils' download_file(), getting the URL from Driver's get_url()
        # method, which uses url, version, name, and os_type from this class'
        # init. (default output would be something like chromedriver.*googleapis.com/81.*/chromedriver_linux64.zip).
        # download_file uses requests and returns File(response).
        # _get_driver_path then uses DriverCache's save_file_to_cache method --
        # BUT THIS IS WHAT WE WANT TO REPLACE!
        driver_path = self._get_driver_path(self.driver)

        os.chmod(driver_path, 0o755)
        # gives read/execute access to everyone and write access to root only

        # make symlink in directory where selenium will check for browser
        if self.driver.get_os_type() in {'linux64', 'linux32', 'mac64', 'mac32'}:
            symlink_src = driver_path #actual_driver_filename equivalent,i think
            # Driver._name (from this class' init args) is equivalent to driver_filename
            symlink_target = os.path.join(self.link_path, self.driver.get_name())
            if os.path.islink(symlink_target):
                if os.path.samefile(symlink_src, symlink_target):
                    log("Symlink already exists: {0} -> {1}".format(symlink_target, symlink_src))
                    return tuple([symlink_src, symlink_target])
                else:
                    log("Symlink {0} already exists and will be overwritten.".format(symlink_target))
                    os.unlink(symlink_target)
            os.symlink(symlink_src, symlink_target)
            log("Created symlink: {0} -> {1}".format(symlink_target, symlink_src))
            st = os.stat(symlink_src)
            os.chmod(symlink_src, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        return tuple([symlink_src, symlink_target])

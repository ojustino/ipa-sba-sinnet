# In Docker images, install webdrivers for selenium to use Chromium/Firefox.

from webdriverdownloader import ChromeDriverDownloader, GeckoDriverDownloader

# install chrom(e|ium) webdriver
cdd = ChromeDriverDownloader()
chromiumdriver, chromiumpath = cdd.download_and_install()
print(chromiumdriver, chromiumpath)

# install firefox webdriver
gdd = GeckoDriverDownloader()
geckodriver, geckopath = gdd.download_and_install("v0.23.0")
print(geckodriver, geckopath)

# (former iteration -- was called install_driver.py)
# Install the proper driver for the browser that selenium will drive headlessly.
# import argparse

# parser = argparse.ArgumentParser(description='set up')
# parser.add_argument('browser', type=str,
#                     help='the browser to use in headless sessions')
# args = parser.parse_args()
# print(args)
# browser = args.browser.lower()

# if browser == 'chrome':
#     from webdriver_manager.chrome import ChromeDriverManager
#     chromepath = ChromeDriverManager().install()
#     print(chromepath)
# elif browser == 'chromium':
#     # from webdriver_chromium_edit import ChromiumDriverManager
#     # chromiumpath = ChromiumDriverManager().install()
#     # from wdd_chromium_edit import ChromiumDriverDownloader # my edit
#     # cdd = ChromiumDriverDownloader()
#     # chromiumdriver, chromiumpath = cdd.download_and_install()
#     from webdriverdownloader import ChromeDriverDownloader
#     cdd = ChromeDriverDownloader()
#     chromiumdriver, chromiumpath = cdd.download_and_install()
#     print(chromiumdriver, chromiumpath)
# elif browser == 'firefox':
#     from webdriverdownloader import GeckoDriverDownloader
#     gdd = GeckoDriverDownloader()
#     geckodriver, geckopath = gdd.download_and_install("v0.23.0")
#     print(geckodriver, geckopath)
# else:
#     raise ValueError('invalid browser. choose from chromium/chrome and firefox')

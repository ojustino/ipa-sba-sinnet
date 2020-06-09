#!/bin/bash

pwd

# download and unpack chromedriver
wget --no-verbose -O /tmp/chromedrivermac_64.zip https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_mac64.zip
unzip -q /tmp/chromedrivermac_64.zip -d ~/bin/
echo "-----chromedriver unzipped-----"

# download and unpack geckodriver (for Firefox)
wget --no-verbose -O /tmp/geckodriver-v0.23.0.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-macos.tar.gz
tar -xzf /tmp/geckodriver-v0.23.0.tar.gz -C ~/bin/
echo "-----geckodriver untarred-----"

# add *drivers' location to path so selenium can find them
export PATH="$PATH:~/bin/"

# download and unpack chromium
wget --no-verbose -O /tmp/chromium-83.0.4103.97.zip https://github.com/macchrome/macstable/releases/download/v83.0.4103.97-r756066-Ungoogled-macOS/Chromium.app.ungoogled-83.0.4103.97.zip
unzip -q /tmp/chromium-83.0.4103.97.zip -d /Applications
echo "-----chromium unzipped-----"

# (.travis.yml already takes care of installing firefox)

# list contents of relevant directories
ls -lt ~/bin
echo "-----------------------"
ls /Applications
echo "-----------------------"
ls /tmp/

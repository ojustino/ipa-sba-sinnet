#!/bin/bash
# Install browsers and webdrivers for selenium in GitHub Actions.

pwd

# download and unpack chromedriver
if [ "$RUNNER_OS" == "Linux" ]; then
    wget --no-verbose -O /tmp/chromedriver-64b.zip https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip
    # last worked with v86.0.4240.22 on Travis
elif [ "$RUNNER_OS" == "macOS" ]; then
    wget --no-verbose -O /tmp/chromedriver-64b.zip https://chromedriver.storage.googleapis.com/93.0.4577.63/chromedriver_mac64.zip
    # last worked with v83.0.4103.39 on Travis
else
    echo "Invalid OS. Windows TBD..."
    # Windows would require a wholly different commands as a non-Unix OS
fi

unzip -q /tmp/chromedriver-64b.zip -d ~/bin/
echo "----^chromedriver unzipped^----"

# download and unpack geckodriver (for Firefox)
if [ "$RUNNER_OS" == "Linux" ]; then
    wget --no-verbose -O /tmp/geckodriver-v0.23.0.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
elif [ "$RUNNER_OS" == "macOS" ]; then
    wget --no-verbose -O /tmp/geckodriver-v0.23.0.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-macos.tar.gz
else
    echo "Invalid OS. Windows TBD..."
fi

tar -xzf /tmp/geckodriver-v0.23.0.tar.gz -C ~/bin/
echo "----^geckodriver untarred^----"

# ~/bin must be added to PATH, but the export PATH method doesn't persist across
# jobs in GitHub Actions! set it in the .yml file instead.

# install (Linux)/download and unpack (Mac) chromium
if [ "$RUNNER_OS" == "Linux" ]; then
    # unlike docker, the Actions linux build comes with chrome pre-installed.
    # uninstall it so it's not chosen by selenium over chromium
    ls -d /usr/bin/go*
    echo "----^/usr/bin/go*^-----"
    sudo apt-get purge chromium-browser google-chrome-stable
    # sudo apt-get -q clean
    # sudo apt-get -q update
    sudo apt-get --yes -qq install chromium-browser
    chromium-browser --version
elif [ "$RUNNER_OS" == "macOS" ]; then
    # uninstall default Chrome and chromedriver to avoid confusion in selenium
    ls -d /Applications/Go*
    echo "--^/Applications/Go*^--"
    sudo rm -r '/Applications/Google Chrome.app' ~/Library/Application Support/Google/Ch* /usr/local/bin/chromedriver
    # wget --no-verbose -O /tmp/chromium-83.0.4103.97.zip https://github.com/macchrome/macstable/releases/download/v83.0.4103.97-r756066-Ungoogled-macOS/Chromium.app.ungoogled-83.0.4103.97.zip
    # wget  --no-verbose -O /tmp/chromium-95.0.4638.54.zip https://github.com/macchrome/macstable/releases/download/v95.0.4638.54-r920003-Ungoogled-macOS/Chromium.app.ungoogled-95.0.4638.54.zip
    wget  --no-verbose -O /tmp/chromium-93.0.4577.63.zip https://github.com/macchrome/macstable/releases/download/v93.0.4577.63-r902210-Ungoogled-macOS/Chromium.app.ungoogled-93.0.4577.63.zip
    unzip -q /tmp/chromium-93.0.4577.63.zip -d /Applications
else
    echo "Invalid OS. Windows TBD..."
fi
echo "----^chromium equipped^----"

# install a specific version of Firefox? .travis.yml used 77.0.1.

# list contents of relevant directories
ls /tmp/
echo "--------^/tmp/^--------"
ls ~/bin
echo "-------^~/bin/^--------"
if [ "$RUNNER_OS" == "macOS" ]; then ls /App*; else ls -d /usr/bin/ch* /usr/bin/go*; fi
echo "--------^apps^---------"
ls /usr/local/bin/ch*
echo "-phantom-chromedriver?-"

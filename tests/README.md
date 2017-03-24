# Setup
1. `sudo pip install splinter pytest`
1. `sudo apt-get install chromium-browser`
1. Download chromedriver and move into path
1. Install phantomjs (note: the version in the Ubuntu repos is broken): `sudo npm -g install phantomjs-prebuilt`

# Run tests
Tests are run with the `pytest` test runner.
2. Run tests `py.test tests`

To use Chrome, change this: browser = `Browser('chrome')`

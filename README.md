# Wyscout scraper

A web scraper for collecting data from https://platform.wyscout.com/app/ website. 

### Install

1. Install Python https://www.python.org/downloads/
2. Install pip to easy install libraries (https://phoenixnap.com/kb/install-pip-mac)
3. Install BeautifulSoup
```
pip install BeautifulSoup
```
4. Install requests
```
pip install requests
```

5. Install Selenium
```
pip install selenium
```

6. Downlaod the chromedriver compatible with your os and current running Chrome browser (check in Settings)
  https://chromedriver.chromium.org/downloads
   <br />

### Usage
1. Run WyscoutBot.py to scrape leagues
   ```
python3 WyscoutBot.py
```
2. Run players.py to retreive player data

3. Run soupify.py to adjust player data

4. Run Matching_Wyscout_FootyStats.py to create a dataset with players data


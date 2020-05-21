# import standard libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# define chrome options
CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

# set options
chrome_options = Options()
chrome_options.binary_location = CHROME_PATH

# open invisible browser
browser = webdriver.Chrome(CHROMEDRIVER_PATH, options = chrome_options)

# set implicit wait for page load
browser.implicitly_wait(10)

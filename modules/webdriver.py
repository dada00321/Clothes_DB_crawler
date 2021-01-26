from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options

class Webdriver():
    def get_webdriver(self, headless):
        chrome_options = Options()
        if headless == True:
            chrome_options.add_argument("--headless")
            #chrome_options.headless = True # also works
        wd_path = r"D:\geckodriver\chromedriver.exe"
        driver = wd.Chrome(wd_path, options=chrome_options)
        driver.implicitly_wait(10)
        return driver
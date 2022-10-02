def get_driver():
    options = webdriver.FirefoxOptions()
    options.binary_location = r"/usr/lib/firefox/firefox-bin"
    driver = webdriver.Firefox(options=options)
    return driver
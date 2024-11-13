# import time
#
# from seleniumwire import webdriver
#
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
#
# # configure the proxy
# proxy_username = "gbGtp7"
# proxy_password = "36cunF"
# proxy_address = "193.31.100.208"
# proxy_port = "9278"
#
# # formulate the proxy url with authentication
# proxy_url = (f"http://{proxy_username}:{proxy_password}@{proxy_address}"
#              f":{proxy_port}")
#
# # set selenium-wire options to use the proxy
# seleniumwire_options = {
#     "proxy": {
#         "http": proxy_url,
#         "https": proxy_url
#     },
# }
#
# # set Chrome options to run in headless mode
# options = Options()
#
# # initialize the Chrome driver with service, selenium-wire options, and chrome options
# driver = webdriver.Chrome(
#     service=Service(
#         executable_path="C:\\chromedriver.exe"
#     ),
#     seleniumwire_options=seleniumwire_options,
#     options=options
# )
#
# # navigate to the target webpage
# driver.get("https://httpbin.io/ip")
#
# # print the body content of the target webpage
# print(driver.find_element(By.TAG_NAME, "body").text)
# time.sleep(180)
# # release the resources and close the browser
# driver.quit()

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

def login(driver, URL):
    path = "login.php"
    driver.get(URL + path)
    driver.find_element(By.NAME, "login").send_keys("bee")
    driver.find_element(By.NAME, "password").send_keys("bug")
    driver.find_element(By.NAME, 'form').click()

#TODO: untested
def firstname_xss(driver: webdriver, full_url: str, payload: str) -> str:
    driver.get(full_url)
    driver.find_element(By.ID, "firstname").send_keys(payload)
    driver.find_element(By.ID, "lastname").send_keys("test")
    driver.find_element(By.NAME, 'form').click()
    return driver.page_source

#TODO: untested
def xss_reflected_get_firstname(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_get.php"
    return firstname_xss(driver, URL + path, payload)

#TODO: untested
def xss_reflected_post_firstname(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_post.php"
    return firstname_xss(driver, URL + path, payload)

#TODO: untested
def xss_reflected_json(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_json.php"
    driver.get(URL + path)
    driver.find_element(By.ID, "title").send_keys(payload)
    driver.find_element(By.NAME, 'action').click()
    html = driver.page_source
    return html

#TODO: untested
def xss_reflected_ajax_json(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_ajax_2-1.php"
    driver.get(URL + path)
    driver.find_element(By.ID, "title").send_keys(payload)
    sleep(1)
    html = driver.page_source
    return html

#TODO: untested
def xss_reflected_ajax_xml(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_ajax_1-1.php"
    driver.get(URL + path)
    driver.find_element(By.ID, "title").send_keys(payload)
    sleep(1)
    html = driver.page_source
    return html

#TODO: how? set referrer header?
def xss_reflected_back_button(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_back_button.php"
    driver.get(URL + path)
    driver.find_element(By.TAG_NAME, 'input').click() #TODO does this work?
    html = driver.page_source
    return html

#TODO: how? set "bWAPP" header?
def xss_reflected_custom_header(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_custom_header.php"
    driver.get(URL + path)
    html = driver.page_source
    return html

#TODO: how? set "bWAPP" header?
def xss_reflected_user_agent_header(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_user_agent.php"
    driver.get(URL + path)
    html = driver.page_source
    return html

#TODO: how? set referrer header?
def xss_reflected_referer_header(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_referer.php"
    driver.get(URL + path)
    html = driver.page_source
    return html

#TODO: untested
def xss_reflected_eval(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_eval.php"
    driver.get(URL + path + "?date=" + payload)
    html = driver.page_source
    return html

#TODO: site seems bugged
def xss_reflected_href(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_href-1.php"
    driver.get(URL + path)
    html = driver.page_source
    return html

#TODO: site seems bugged
def xss_reflected_php_self(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_php_self.php"
    return firstname_xss(driver, URL + path, payload)

#TODO: untested
def xss_stored_blog(driver: webdriver, URL: str, payload: str) -> str:
    path = "xss_stored_1.php"
    driver.get(URL + path)
    driver.find_element(By.ID, "entry").send_keys(payload)
    driver.find_element(By.NAME, 'blog').click()
    html = driver.page_source

    # delete entry again to make the web app ready for another payload
    driver.find_element(By.ID, "entry_add").click()
    driver.find_element(By.ID, "entry_delete").click()
    driver.find_element(By.NAME, 'blog').click()

    return html

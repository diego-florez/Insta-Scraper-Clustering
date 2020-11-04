#*********************************** PACKAGES ************************************

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup 
import time
import re
from urllib.request import urlopen
import pandas as pd, numpy as np

from  more_itertools import unique_everseen
from IPython.display import clear_output

import csv

#*********************************** CLASS ************************************

class InstagramScraper():


    def __init__(self, hashtags=[]):
        self.hashtags = hashtags


    def scrapeLinks(self, driver, url, hashtag):
        driver.get(url)
        #check number of posts
        try:
            posts = driver.find_element_by_xpath("//span[contains(@class, 'g47SY ')]").text
            print(f"Loading Page For #{hashtag}...\n\n Number of Posts: {posts}")
        except NoSuchElementException:
            print(f"Loading Page For #{hashtag}...\n\n Number of Posts: Not Found")
        #gets scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        #initiate empty list for unique Instagram links
        links = []

        #some lines for user interactivity / selection of link target(n)
        print("\n")
        target = input("How many Posts do you want to scrape (max)?: ")
        print("\n")
        print("Starting Selenium scrape, please keep browser open.")
        print("\n")

        #this loops round until n links achieved or page has ended

        while True:

            source = driver.page_source
            data = BeautifulSoup(source, 'html.parser')
            body = data.find('body')

            #script = body.find('span')
            for link in body.findAll('a'):
                if re.match("/p", link.get('href')):
                    links.append('https://www.instagram.com'+link.get('href'))
                else:
                    continue

            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")

            #if no more content, scrape loop is terminated
            if new_height == last_height:
                break
            last_height = new_height

            #update on successful links scraped
            print("Scraped ", len(links)," links, ", len(set(links)),' are unique')

            #if n target met then while loop breaks
            if len(set(links)) > int(target):
                break

        #Unique links are saved
        links_unique = list(unique_everseen(links))

        #clear the screen and provide user feedback on performance
        clear_output()

        print("Finished scraping links. Maxed out at ", len(links)," links, of which ", len(links_unique),' are unique.\n')

        print("Unique links obtained\n\n")

        return links_unique



    def scrapeComments(self, links, driver, wait):

        #list to add all users from comments
        comments_users = []

        #list to add all users from answers
        #answers_users = []

        #list to add all comments
        all_comments = []

        #list to add commenters picture's profile
        all_pictures = []

        #loop to obtain all elements
        for i, l in enumerate(links):
            print(f"\nScraping Link {i}\n")
            driver.get(l)

            while True:
                
                #load more comments/answers
                try:
                    #load all comments
                    more_comments = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dCJp8 afkep')]")))
                    ActionChains(driver).move_to_element(more_comments).click().perform()
                    print("Loading More Comments...")

                    #wait 2 seconds for all comments to be loaded
                    time.sleep(2)

                    #load comments answers
                    all_answers = driver.find_elements_by_xpath("//span[contains(@class, 'EizgU')]")
                    if all_answers == []:
                        print("No + Answers to Load\n")
                    else:
                        try:
                            for answer in all_answers:
                                answer.click()
                            print("Loading Answers...\n")
                        except Exception:
                            print("No + Answers to Load\n")

                    #wait 2 seconds for all comments to be loaded
                    time.sleep(2)

                    #getting all @users who commented on the post
                    try:
                        users = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//a[contains(@class, 'sqdOP')]")
                        users = [user.get_attribute("href") for user in users]
                        comments_users.extend(users)
                        print(f"Users Who Commented in link {i} Added:", users)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        comments_users.extend(np.nan)

                    #getting all @users who answered on the post
                    """try:
                        answers = driver.find_elements_by_xpath("//ul[contains(@class, 'TCSYW')]//span[contains(@class, 'EizgU')]")
                        answers = [user.text for user in answers]
                        answers_users.extend(answers)
                        print(f"Users Who Answered in link {i} Added:", answers)
                    except NoSuchElementException:
                        print("This Post doesn't have any answers")
                        answers_users.extend(np.nan)"""

                    #getting all users profile's picture
                    try:
                        pictures = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//img[contains(@class, '_6q-tv')]")
                        pictures = [picture.get_attribute("src") for picture in pictures]
                        all_pictures.extend(pictures)
                        print(f"Profile's Pictures from Users Who Commented in link {i} Added:", pictures)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        all_pictures.extend(np.nan)

                    #getting all comments
                    try:
                        comments = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//div[contains(@class, 'C4VMK')]/span")
                        comments = [comment.text for comment in comments]
                        all_comments.extend(comments)
                        print(f"Comments in link {i} Added:", comments)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        all_comments.extend(np.nan)

                #in case of no more comments and/or answers
                except TimeoutException:
                    print("No + Comments to Load\n")

                    #load comments answers
                    all_answers = driver.find_elements_by_xpath("//span[contains(@class, 'EizgU')]")
                    if all_answers == []:
                        print("No + Answers to Load\n")
                    else:
                        try:
                            for answer in all_answers:
                                answer.click()
                            print("Loading Answers...\n")
                        except Exception:
                            print("No + Answers to Load\n")

                    #wait 2 seconds for all comments to be loaded
                    time.sleep(2)

                    #getting all @users who commented on the post
                    try:
                        users = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//a[contains(@class, 'sqdOP')]")
                        users = [user.get_attribute("href") for user in users]
                        comments_users.extend(users)
                        print(f"Users Who Commented in link {i} Added:", users)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        comments_users.extend(np.nan)

                    #getting all @users who answered on the post
                    """"try:
                        answers = driver.find_elements_by_xpath("//ul[contains(@class, 'TCSYW')]//span[contains(@class, 'EizgU')]")
                        answers = [user.text for user in answers]
                        answers_users.extend(answers)
                        print(f"Users Who Answered in link {i} Added:", answers)
                    except NoSuchElementException:
                        print("This Post doesn't have any answers")
                        answers_users.extend(np.nan)"""

                    #getting all users profile's picture
                    try:
                        pictures = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//img[contains(@class, '_6q-tv')]")
                        pictures = [picture.get_attribute("src") for picture in pictures]
                        all_pictures.extend(pictures)
                        print(f"Profile's Pictures from Users Who Commented in link {i} Added:", pictures)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        all_pictures.extend(np.nan)

                    #getting all comments
                    try:
                        comments = driver.find_elements_by_xpath("//ul[contains(@class, 'Mr508')]//div[contains(@class, 'C4VMK')]/span")
                        comments = [comment.text for comment in comments]
                        all_comments.extend(comments)
                        print(f"Comments in link {i} Added:", comments)
                    except NoSuchElementException:
                        print("This Post doesn't have any comments")
                        all_comments.extend(np.nan)

                break

        return comments_users, all_comments, all_pictures


    def saveCsv(self, hashtag, users, comments, pictures):

        #saving in csv
        with open("".join([hashtag.replace(" ","-"), ".csv"]), 'w', newline='') as csvfile:
            fieldnames = ["users", "comments", "pictures"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for user, comment, picture in zip(users, comments, pictures):
                writer.writerow({"users":user, "comments":comment, "pictures":picture})
        print("\n\n","".join(["#",hashtag.replace(" ","-"), " Users, Comments & Pictures Scraped from Instagram"]))

        

    def lookUp(self, hashtags):
        #setting driver
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument('--disable-gpu')
        options.add_argument("--start-maximized")
        #pass url
        for hashtag in hashtags:
            url = ('https://www.instagram.com/explore/tags/'+hashtag)
            driver = webdriver.Chrome(options=options)
            #wait parameter
            wait = WebDriverWait(driver, 5)
            #script
            post_links = self.scrapeLinks(driver, url, hashtag)
            users, comments, pictures = self.scrapeComments(post_links, driver, wait)
            self.saveCsv(hashtag, users, comments, pictures)
            # close driver
            driver.quit()
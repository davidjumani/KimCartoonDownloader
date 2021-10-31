#!/usr/bin/env python3

import json
import os
import re
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class KimCartoon :
    def __init__(self, creds) :
        self.driver = webdriver.Chrome()
        self.driver.delete_all_cookies();
        self.driver.set_page_load_timeout(15)
        self.creds = creds

    def login(self) :
        self.driver.delete_all_cookies();
        url = 'http://kimcartoon.li/Login'
        print("Loading login page")
        try :
            self.driver.get(url)
        except Exception as e :
            pass

        try :
            element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        except Exception as e :
            self.quit_and_log(url, e)

        current_tab = self.driver.window_handles[0]
        print("Loging in")
        self.wait(5)
        username = self.driver.find_element(By.ID, "username")
        password =self.driver.find_element(By.ID, "password")
        chk_remember = self.driver.find_element(By.ID, "chkRemember")
        submit = self.driver.find_element(By.ID, "btnSubmit")

        username.send_keys(self.creds['username'])
        password.send_keys(self.creds['password'])
        chk_remember.click()
        try :
            submit.click()
        except :
            pass

        try :
            # Handle popups
            print("Handling popups")
            self.wait(2)
            self.driver.switch_to.window(current_tab)
            # for handle in self.driver.window_handles[1:]:
            #     self.driver.switch_to.window(handle)
            #     self.driver.close()
            print("Handled popups")
            self.wait(5)
        except Exception as e :
            self.quit_and_log(url, e)

    def get_episodes_list(self, url) :
        print("Getting episodes from : %s" %(url))
        try :
            self.driver.get(url)
        except :
            pass

        self.wait(5)
        links = {}
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "listing"))
            )
            urls = self.driver.find_elements(By.XPATH, '//table//a')
            regex = re.compile(r'.*[?]id=[0-9]+$', re.I)
            for url in urls :
                try :
                    link = url.get_attribute('href')
                    if regex.match(link)  :
                        links[url.text.strip()] = link
                except :
                    continue
            print("Got %d episodes" %len(links))
            return links
        except Exception as e :
            self.quit_and_log(url, e)

    def get_all_download_links(self, links, skip) :
        episodes = {}
        num = 1
        for name in sorted(links) :
            if num < skip :
                num = num + 1
                print("Skipping %s" %(name))
                continue
            print("[%d] " %(num), end="", flush=True)
            episodes[name] = self.get_download_links(links[name])
            print("Got %d episode links so far :" %(len(episodes)))
            print(json.dumps(episodes, sort_keys=True))
            print()
            num = num + 1
        return episodes

    def get_download_links(self, url) :
        print("Getting download links from : %s" %(url))
        try :
            self.driver.get(url)
        except :
            pass

        self.wait(5)
        donwload_links = {}
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "divDownload"))
            )
            links = element.find_elements(By.TAG_NAME, 'a')
            print("Got %d download link(s)" %len(links))
            if len(links) == 1 :
                donwload_links = links[0].get_attribute('href')
            else :
                for link in links :
                    donwload_links[link.text] = link.get_attribute('href')
        except :
            print("FAILED get %s" %(url))
            print(self.driver.current_url)

        self.wait(5)
        return donwload_links

    def wait(self, seconds) :
        for i in range(seconds) :
            print(".", end =" ", flush=True)
            time.sleep(1)
        print()

    def quit(self) :
        print("Quitting!")
        self.driver.quit()
        time.sleep(2)

    def quit_and_log(self, url, e) :
        print(e)
        print("FAILED get %s" %(url))
        print(self.driver.current_url)
        self.quit()
        sys.exit(1)

    # def __del__(self) :
    #   self.quit()


def main() :
    with open('creds.json') as file :
        creds = json.loads(file.read())

    url = sys.argv[1]
    browser = KimCartoon(creds)
    links = browser.get_episodes_list(url)
    print("Got episodes : ")
    print(json.dumps(links))
    print()
    browser.login()
    skip = 0
    print()
    print("Starting to fetch links")
    episodes = browser.get_all_download_links(links, skip)
    print()
    browser.quit()
    print()
    print("All %d episodes download links :" %(len(links)))
    print(json.dumps(episodes))
    print()

if __name__ == "__main__" :
    main()

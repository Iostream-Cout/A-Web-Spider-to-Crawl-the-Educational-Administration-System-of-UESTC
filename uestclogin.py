# -*- coding: utf-8 -*-

import requests
import urlparse
import os
import json
import bs4
import re

# Constants used during the crawling process
LOG_URL = 'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/index.portal'
GRADE_URL = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR'
COOKIE_PATH = 'Cookie.txt'
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"}


# The main class used to log into the system
class Login(object):
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        # To create a session for the access of this time
        self.__session = requests.Session()
        # To get the cookies created during the last access
        cookies = self.__getCookies()
        # To add the cookies into the cookiejar inside the session
        if cookies:
            requests.utils.add_dict_to_cookiejar(self.__session.cookies,
                                                 cookies)

    # A static method to get the cookies created during the last access
    @staticmethod
    def __getCookies():
        # To check whether the cookie file exists.
        # if not, return None.
        if not os.path.exists(COOKIE_PATH):
            return None
        # To create a file handler and read the file
        fileHand = open(COOKIE_PATH)
        json_cookies = fileHand.read()
        # If it is an empty file, then return None.
        if not json_cookies:
            return None
        # To transform the json based string data into a Dict
        cookies = json.loads(json_cookies)
        fileHand.close()
        # To return the cookie data stored in a Dict
        return cookies

    # The method used to log into the system
    def log(self, url):
        session = self.__session
        # To clear up the cookie to prevent the website from using the
        # cookies to fill the form.
        session.cookies.clear()
        # To visit the login page
        response = session.get(url, headers=HEADERS)
        # To initialize a soup using the page HTML
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        # To find the login form
        form = soup.find('form', class_='fm-v clearfix amp-login-form')
        # To get the url we need to post the form
        post_url = form['action']
        post_url = urlparse.urljoin(url, post_url)
        # To find the four hidden input objects and get their randomly generated values
        lt = soup.find('input', attrs={'name': 'lt'})['value']
        dllt = soup.find('input', attrs={'name': 'dllt'})['value']
        execution = soup.find('input', attrs={'name': 'execution'})['value']
        eventid = soup.find('input', attrs={'name': '_eventId'})['value']
        rmShown = soup.find('input', attrs={'name': 'rmShown'})['value']
        data = dict()
        data['username'] = self.__username
        data['password'] = self.__password
        data['lt'] = lt
        data['execution'] = execution
        data['dllt'] = dllt
        data['_eventId'] = eventid
        data['rmShown'] = rmShown
        # To post the form to the aimed url and return the response
        return session.post(post_url, data=data, headers=HEADERS)

    # The method to visit a page inside the system
    def visit(self, url):
        # An attempt to visit the page
        r = self.__session.get(url, headers=HEADERS)
        # To check the response to judge whether another login operation
        # should be done.
        flag = self.__out_of_log(r)
        if not flag:
            return r
        if flag == 1:
            self.log(LOG_URL)
            return self.visit(url)
        return self.visit(flag)

    # A static method to check if the session has done the login operation
    # or if it has been expired.
    @staticmethod
    def __out_of_log(r):
        if r.url == LOG_URL:
            return 1
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        if re.match(u"本次会话已经被过期.*", soup.text):
            return 1
        title = soup.find('title')
        if title is not None and title.text == u'电子科技大学登录':
            return 1
        a = soup.find('a', text='点击此处')
        if a is not None:
            return a['href']
        return 0

    # To close the Login object
    def close(self):
        fileHand = open(COOKIE_PATH, 'w')
        # The cookies need to be saved
        fileHand.write(str(requests.utils.dict_from_cookiejar(self.__session.cookies)).replace("'", '"').replace('u"', '"'))
        fileHand.close()

# A method to get grade of a certain course
def getGrade(username, password, name):
    login = Login(username, password)
    try:
        r = login.visit(GRADE_URL)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        table = soup.find_all('table', class_='gridtable')[1]
        tbody = table.tbody
        for tr in tbody:
            if tr.contents[7].get_text().strip() != name:
                continue
            return int(tr.contents[14].get_text())
        return None
    finally:
        login.close()
		
def getGPA(username, password):
    login = Login(username, password)
    try:
        grade_page = login.visit(GRADE_URL)
        soup = bs4.BeautifulSoup(grade_page.text, 'html.parser')
        gpa_table = soup.find('table', class_='gridtable')
        tbody = gpa_table.tbody
        tr = tbody.contents[-4]
        return float(tr.contents[-2].text)
    finally:
        login.close()

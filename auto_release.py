# -*- coding: utf-8 -*- 
import sys
import pymysql
import time
import random
from selenium import webdriver
reload(sys)
sys.setdefaultencoding('utf-8')


class Auto_release(object):
    def __init__(self):
        # if self.user_data['auto_release'] == 'on':
        # while True:
            web_users = self.get_web_users()
            for web_user in web_users:
                print web_user['user_name']
                self.user_data = self.get_user_data(web_user['user_name'])
                self.gap = self.user_data['gap']
                self.auto_release(self.user_data, web_user['user_name'])
                time.sleep(10)

                check=self.check_auto_release(web_user['user_name'])
                if check == False:
                    break
                time.sleep(self.gap-10)
    def get_web_users(self):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                sql = """SELECT `user_name`, `account`, `password`, `auto_release`, `ran_or_new`, `gap` FROM `weibo_info` WHERE auto_release='on'"""
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
            connection.commit()

        finally:
            connection.close()       

    def get_user_data(self, web_user):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                sql = """SELECT `user_name`, `account`, `password`, `auto_release`, `ran_or_new`, `gap` FROM `weibo_info` WHERE user_name='{}'""".format(web_user)
                cursor.execute(sql)
                result = cursor.fetchone()
                return result
            connection.commit()

        finally:
            connection.close()

    def get_release_data(self, ran_or_new, web_user):
        connection = pymysql.connect(
        host='localhost',
        user='root',
        password='henry!QAZ@WSX',
        db='scrapyDB',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                if ran_or_new == 'ran':
                    today = time.strftime("%Y-%m-%d", time.localtime())
                    sql = """SELECT `title`, `content`, `time`, `url`, `who_release` FROM `news` WHERE DATE(time)='{}'""".format(today)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    no_release_data = []
                    for item in result:
                        if item['who_release'] == web_user:
                            pass
                        else:
                            no_release_data.append(item)
                    ran_data = random.choice(no_release_data)
                    data = []
                    data.append(ran_data)
                    return data
                else:
                    sql = """SELECT `title`, `content`, `time`, `url`, `who_release` FROM `news` ORDER BY `time` DESC"""
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    no_release_data = []
                    for item in result:
                        if item['who_release'] == web_user:
                            pass
                        else:
                            no_release_data.append(item)
                            break
                    return no_release_data
            connection.commit()

        finally:
            connection.close()

    def check_auto_release(self, web_user):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                
                sql = """SELECT `auto_release` FROM `weibo_info` WHERE user_name='{}'""".format(web_user)
                cursor.execute(sql)
                result = cursor.fetchone()
                if result['auto_release'] != 'on':
                    return False
                print('檢查有過')
            connection.commit()

        finally:
            connection.close()

    def auto_release(self, user_data, web_user):
        user_account = user_data['account']
        user_password = user_data['password']
        ran_or_new = user_data['ran_or_new']

        release_data = self.get_release_data(ran_or_new, web_user)
        news_title = release_data[0]['title']
        news_content = release_data[0]['content']
        news_url = release_data[0]['url']
        # time = release_data[0]['time']
        who_release = release_data[0]['who_release']

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('window-size=1200,1100');
        # chromedriver = "/usr/local/share/chromedriver"
        # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver)
        browser = webdriver.Chrome()

        browser.maximize_window()

        browser.implicitly_wait(10)
        browser.get('https://www.weibo.com/login.php')

        print browser.title

        username = browser.find_element_by_id('loginname')
        pwd = browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')
        print ('輸入帳號密碼')
        username.send_keys(user_account)
        time.sleep(1)
        pwd.send_keys(user_password)
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
        print ('按下登入紐')

        browser.find_element_by_xpath('//div[@class="gn_logo"]/a').click()
        # 數入訊息
        time.sleep(2)
        print ('輸入訊息')
        send_box = browser.find_element_by_xpath('//textarea[@class="W_input"]')
        # send_box.send_keys(textarea_content)
        # send_box.send_keys(u'\ue007')
        # time.sleep(1)
        send_box.send_keys(news_title)
        send_box.send_keys(u'\ue007')
        time.sleep(1)
        send_box.send_keys(news_content)
        send_box.send_keys(u'\ue007')
        time.sleep(1)
        # 按下送出訊息
        browser.find_element_by_xpath('//div[@id="v6_pl_content_publishertop"]/div/div[3]/div[1]/a').click()
        time.sleep(3)
        browser.quit()
        self.insert_who_release(news_url, web_user)
        print ('自動寫入完成')

    def insert_who_release(self, news_url, web_user):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                who_release = self.get_who_release(news_url)
                if who_release[0]['who_release']=='':
                    who_release[0]['who_release']+='{}'.format(web_user)
                else:
                    who_release[0]['who_release']+=',{}'.format(web_user)
                who_release = who_release[0]['who_release']
                sql = """UPDATE news SET who_release='{}' WHERE url='{}'""".format(who_release, news_url)

                cursor.execute(sql)
                
            connection.commit()

        finally:
            connection.close()

    def get_who_release(self, news_url):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                
                sql = """SELECT who_release FROM news where url ='{}' """.format(news_url)
                cursor.execute(sql)
                who_release = cursor.fetchall()
                return who_release                
            connection.commit()

        finally:
            connection.close()

if __name__ == '__main__':
    Auto_release()
            
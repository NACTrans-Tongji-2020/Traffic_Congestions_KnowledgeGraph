# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WeiboLogin():
    def __init__(self, username, password):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        self.browser = webdriver.Chrome()
        self.browser.set_window_size(1050, 840)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def run(self):
        """
        破解入口
        :return:
        """
        self.open()
        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located(
                (By.ID, 'app')
            )
        )
        cookies = self.browser.get_cookies()
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        cookie_str = '; '.join(item for item in cookie)
        self.browser.quit()
        return cookie_str


if __name__ == '__main__':
    # 在目录中放置一个account.txt文件，格式需要与account_sample.txt相同
    # 其实就是把www.xiaohao.fun买的账号复制到新建的account.txt文件中
    root_path = os.path.dirname(os.path.realpath(__file__))
    file_path = root_path + '\\account.txt'
    db_path = root_path + '\\coockie_db.csv'
    if "coockie_db.csv" not in os.listdir(root_path):
        db = pd.DataFrame(columns=('username','password','coockie','status'))
    else:
        db = pd.read_csv(db_path)
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        print('=' * 10 + username + '=' * 10)
        try:
            cookie_str = WeiboLogin(username, password).run()
        except Exception as e:
            print(e)
            continue
        print('获取cookie成功')
        if username in db.username.to_list():
            db.loc[db.username==username] = pd.DataFrame({"username": [username], "password": [password], "coockie": [cookie_str], "status": ["success"]},sort=False)
        else:
            db = db.append(pd.DataFrame({"username": [username], "password": [password], "coockie": [cookie_str], "status": ["success"]}),sort=False)
        db.to_csv(db_path,encoding='utf-8',index=False)
        print('Coockie信息存储成功!')


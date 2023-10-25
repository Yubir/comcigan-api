from flask import Flask, jsonify
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def search_schools(schoolsearch):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # 크드 숨기기

    driver = webdriver.Chrome(options=options)
    try:
        driver.get('http://comci.net:4082/st')

        search_box = driver.find_element(By.ID, 'sc')
        search_box.clear()
        search_box.send_keys(schoolsearch)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="검색"]')))
        search_button.click()

        time.sleep(0.1)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a')))

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        a_tags = soup.find_all('a', {'onclick': True})

        schools_list=[]

        if a_tags:
            for a_tag in a_tags:
                if "없으면 추가 검색하세요" not in a_tag.text:
                    schools_list.append(a_tag.text)
            return schools_list
        
        else:
            return None
    except Exception as e:
        print(f'오류발생 \n {e}')
        return "오류가 발생했습니다."

@app.route('/ss/<schoolsearch>', methods=['GET'])
def search_school_route(schoolsearch):
    schools_list = search_schools(schoolsearch)
    if schools_list:
        return jsonify({'schools': schools_list}), 200 
    else:
        return jsonify({'error': 'No school found'}), 404 

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
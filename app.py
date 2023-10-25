from flask import Flask, jsonify, request, Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def find_school_schedule(school, classs):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # 크드 숨기기

    driver = webdriver.Chrome(options=options)

    try:
        driver.get('http://comci.net:4082/st')

        search_box = driver.find_element(By.ID, 'sc')
        search_box.clear()
        search_box.send_keys(school)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="검색"]')))
        search_button.click()

        a_tags = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@onclick]')))
        
        if a_tags[0].text == school:
            a_tags[0].click()

            classs_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ba"]')))
            classs_select.click()

            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ba"]')))

            try:
                option = select_element.find_element(By.XPATH, f"//option[text()='{classs}']")
                option.click()
            except:
                return None

        schedule = []
        soup = BeautifulSoup(driver.page_source, 'html.parser', from_encoding='utf-8')
        for i in range(1, 7):
            row = []
            for j in range(2, 11):
                cell = soup.select_one(f'#hour > table > tbody > tr:nth-child({j}) > td:nth-child({i})')
                for br in cell.find_all('br'): # <br> 태그를 공백 문자로 바꾸어 띄어쓰기 추가
                    br.replace_with('|')
                row.append(cell.get_text().strip()) # 앞뒤 공백 제거
            schedule.append(row)
        return schedule
    except Exception as e:
        print(f'오류발생 \n {e}')
        return "오류가 발생했습니다."

def search_schools(schoolsearch):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # 크드 숨기기

    driver = webdriver.Chrome(options=options)

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

@app.route('/sp/<school>/<classs>', methods=['GET'])
def get_school_schedule(school, classs):
    schedule = find_school_schedule(school, classs)
    if schedule is not None:
        json_data = json.dumps({'schedule': schedule}, ensure_ascii=False)
        response = Response(json_data, content_type='application/json; charset=utf-8')
        return response
    else:
        json_data = json.dumps({'error': '학교 또는 학년을 찾을 수 없습니다.'}, ensure_ascii=False)
        response = Response(json_data, content_type='application/json; charset=utf-8')
        return response, 404
    
@app.route('/ss/<schoolsearch>', methods=['GET'])
def search_school_route(schoolsearch):
    schools_list = search_schools(schoolsearch)
    if schools_list:
        return jsonify({'schools': schools_list}), 200 
    else:
        return jsonify({'error': '학교를 찾을 수 없습니다.'}), 404 

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
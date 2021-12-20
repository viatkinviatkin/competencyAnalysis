import nltk
from nltk.probability import FreqDist
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt 
import numpy as np
from collections import Counter
import itertools
import re

JOB = 'программист'
QUERY = 'https://perm.hh.ru/search/vacancy?clusters=true&area=72&ored_clusters=true&enable_snippets=true&salary=&text='

def connect(url):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--log-level=3') ## remove warining
    options.add_argument("--headless")
    #options.add_argument("user-agent=whatever you want")
    driver = webdriver.Chrome(executable_path="C:\chromedriver\chromedriver.exe", chrome_options=options)
    driver.get(url)
    return driver

def barChart(dict1):
    x = list(dict1.keys())
    y = list(dict1.values())
    color_rectangle = np.random.rand(7, 3)
    fig, ax = plt.subplots()
    color_rectangle = np.random.rand(7, 3)    # RGB
    ax.bar(x, y, color = color_rectangle, edgecolor = 'darkblue', linewidth = 3)
    fig.set_figwidth(12)    #  ширина и
    fig.set_figheight(6)    #  высота "Figure"
    fig.set_facecolor('floralwhite')
    ax.set_facecolor('seashell')
    jobName = str(f'{JOB}ом')
    plt.title('Наиболее востребованные компетенции\nсреди предложений о работе '+ r"$\bf{" + jobName + "}$\n"+'на сайте hh.ru')
    plt.xlabel('Компетенции')
    plt.ylabel('Востребованность')
    plt.show()

def WriteFile(fileName, freqDictionary):
    with open(fileName, "w", encoding='utf-8') as output:
        for f in freqDictionary:
            output.write(f + ', ' + str(freqDictionary[f]) + '\n' )


driver = connect(QUERY+JOB)
vacancies = []
for vacancy_DOM_element in driver.find_elements(By.CLASS_NAME,'vacancy-serp-item'):
    vacancies.append(vacancy_DOM_element.find_element(By.CLASS_NAME,'bloko-link').get_attribute('href'))
driver.quit()

skills = []
skills_salary = {}
for vacancy in vacancies:
    driver = connect(vacancy)
    skills_DOM = [element.get_attribute('textContent') for element in driver.find_elements(By.CLASS_NAME, 'bloko-tag__section.bloko-tag__section_text')]
    skills.append(skills_DOM)

    # #Величина зп от компетенций
    # salary_DOM = driver.find_element(By.CSS_SELECTOR, 'span.bloko-header-2.bloko-header-2_lite')
    # test = salary_DOM.get_attribute('textContent').split()
    # test = ''.join(test)
    # salary = re.findall("\d+",test)[0] 
    # anonymous_object = type('',(),{'skills':skills_DOM, 'salary':salary})()
    # print(anonymous_object.salary)
    # #########################

    driver.quit()
print(skills)

all_skills_together = []
for microarray in skills:
    for skill in microarray:
        if(skill!=''):
            for s in skill.split(','):
                all_skills_together.append(s) 

freq = FreqDist(all_skills_together)
WriteFile('freqsSkills.txt',freq)

sortbyfreqs = {k: v for k, v in sorted(freq.items(), key=lambda item: item[1], reverse=True)}
barChart(dict(itertools.islice(sortbyfreqs.items(), 10)))

#Зависимость компетенций от величины зп




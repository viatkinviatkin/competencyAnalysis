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
import sqlite3

JOB = 'повар'
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

def bar_chart(dict1):
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
    ax.set_xticklabels(x, rotation=45)
    jobName = str(f'{JOB}ом')
    plt.title('Наиболее востребованные компетенции\nсреди предложений о работе '+ r"$\bf{" + jobName + "}$\n"+'на сайте hh.ru')
    plt.xlabel('Компетенции')
    plt.ylabel('Востребованность')
    plt.show()

def salary_barchart(dict1, dict2):

    x = list(dict1.keys())
    y1 = list(dict1.values())
    y2 = list(dict2.values())
    
    fig, ax = plt.subplots()
    color_rectangle = np.random.rand(7, 3)    # RGB
    
    ax.bar(x, y1, color = color_rectangle, width = 0.5)
    color_rectangle = np.random.rand(7, 4)    # RGBA
    color_rectangle[:,3] = 0.5
    ax.set_xticklabels(x, rotation=45)
    ax.bar(x, y2, color = color_rectangle)
    fig.set_figwidth(12)    #  ширина и
    fig.set_figheight(6)    #  высота "Figure"
    fig.set_facecolor('floralwhite')
    ax.set_facecolor('seashell')
    ax.set_xticklabels(x, rotation=45)
    plt.xlabel('Уровень ЗП от наличия компетенций')
    plt.ylabel('Уровень ЗП в руб.')
    plt.xlabel('Компетенции')
    plt.style.use('ggplot')
    plt.show()

def write_file(fileName, freqDictionary):
    with open(fileName, "w", encoding='utf-8') as output:
        for f in freqDictionary:
            output.write(f + ', ' + str(freqDictionary[f]) + '\n' )

def get_salary(salary_DOM):
    dirty_salary_value = salary_DOM.get_attribute('textContent')
    salary = dirty_salary_value.split()
    salary = ''.join(salary)
    salary = int(re.findall("\d+",salary)[0])

    if (dirty_salary_value.find('USD')!= -1):
        print('В элементе',dirty_salary_value,'Нашел usd!')
        salary *=73
    if (dirty_salary_value.find('EUR')!= -1):
        print(dirty_salary_value, 'Нашел eur!')
        salary *=83
    
    return salary



driver = connect(QUERY+JOB)
vacancies = []
for vacancy_DOM_element in driver.find_elements(By.CLASS_NAME,'vacancy-serp-item'):
    vacancies.append(vacancy_DOM_element.find_element(By.CLASS_NAME,'bloko-link').get_attribute('href'))
for vacancy in vacancies: print(vacancy)
driver.quit()

competencies = []
skills_salary = []
sqlite_connection = sqlite3.connect('analysisHH.db')
for vacancy in vacancies[:8:]:
    driver = connect(vacancy)
    try:
        skills_select = [element.get_attribute('textContent') for element in driver.find_elements(By.CLASS_NAME, 'bloko-tag__section.bloko-tag__section_text')]
        competencies.append(skills_select)

        #Уровень ЗП для компетенций
        salary_DOM = driver.find_element(By.CSS_SELECTOR, 'span.bloko-header-2.bloko-header-2_lite')
        salary = get_salary(salary_DOM)

        #DB табличка вакансия-зп
        # insert vacancy,salary into table1
        
        sqlite_connection.execute(f"INSERT INTO JobOpenings (LinkHH, Salary) VALUES('{vacancy}', {salary})")
        
   

        for skill in skills_select:
            print('skill',skill,'salary', salary)
            skills_salary_obj = type('',(),{'skill':skill, 'salary':salary})()
            skills_salary.append(skills_salary_obj)
            cur = sqlite_connection.cursor()
            cur.execute(f"SELECT * FROM Competency WHERE Name = '{skill}'")
            rows = cur.fetchall()
            if(len(rows) == 0):
                sqlite_connection.execute(f"INSERT INTO Competency (Name) VALUES('{skill}')")
                sqlite_connection.commit()
            sqlite_connection.execute(f"INSERT INTO refJobCompetency (JobID, CompetID) VALUES((SELECT ID FROM JobOpenings WHERE LinkHH = '{vacancy}'), (SELECT ID FROM Competency WHERE Name = '{skill}'))")
            sqlite_connection.commit()
            cur.close()
            
    except:
        print('Не удалось спарсить')
    driver.quit()

print('\nКомпетенции\n', competencies)

all_skills = []
for competency in competencies:
    for skill in competency:
        if(skill!=''):
            for s in skill.split(','):
                all_skills.append(s.lower()) 

freq = FreqDist(all_skills)
write_file('freqsSkills.txt', freq)

sortbyfreqs = {k: v for k, v in sorted(freq.items(), key=lambda item: item[1], reverse=True)}
bar_chart(dict(itertools.islice(sortbyfreqs.items(), 10)))

#Зависимость компетенций от величины зп
result_avg = []
result_max = []
for skills_salary_obj in skills_salary:
    skill = skills_salary_obj.skill

    if (skill in [obj.skill for obj in result_avg]):
        continue

    skill_salary_list = [obj.salary for obj in skills_salary if obj.skill == skill]

    max_skill_salary = max(skill_salary_list)
    result_max.append(type('',(),{'skill':skills_salary_obj.skill, 'max_salary':max_skill_salary})())

    avg_skill_salary = round(sum(skill_salary_list)/len(skill_salary_list))
    result_avg.append(type('',(),{'skill':skills_salary_obj.skill, 'avg_salary':avg_skill_salary})())

dict_result_avg ={}
dict_result_max = {}

for obj in result_max: dict_result_max[obj.skill] = obj.max_salary
for obj in result_avg: dict_result_avg[obj.skill] = obj.avg_salary

salary_barchart(dict(itertools.islice(dict_result_avg.items(), 10)),dict(itertools.islice(dict_result_max.items(), 10)))

# #DB компетенция - max_salary
# for obj in result_max:
#     print('skill',obj.skill,'max_salary',obj.max_salary)

# #DB компетенция - avg_salary
# for obj in result_avg:
#     print('skill',obj.skill,'avg_salary',obj.avg_salary)


# #DB компетенция - частотность
# for row in freq:
#     print('key',freq[row],'value',row)

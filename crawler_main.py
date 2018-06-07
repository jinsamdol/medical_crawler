from IPython.display import Image
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import pandas as pd



q_cond = 'Metastatic+Cancer'
q_term = 'drug'
res_file = q_cond+'_'+q_term+'.csv'


driver = webdriver.Chrome('D:\PycharmProjects\crawler\chromedriver')
driver.get("https://clinicaltrials.gov/ct2/results?cond="+q_cond+"&term="+q_term+"&cntry=&state=&city=&dist=")

cthome = "https://clinicaltrials.gov"

urls = []

while 1:
#for i in range(0,1):

    time.sleep(1)

    html = driver.page_source
    bs = BeautifulSoup(html, 'html.parser')

    tb = bs.find_all("a")
    print (len(tb))
    for ss in tb:
        s2 = str(ss.get("href"))

        if re.search("ct2/show/NCT", s2):
            print(s2)
            urls.append(cthome + s2)

    try:

        nbtn = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "theDataTable_next")))


        ss = str(nbtn.get_attribute("class"))

        if ss.endswith('disabled'):
            print('no more pages')
            break
        else:
            nbtn.click()
            print ('move to the next page')

    except:
        print ('error: next button click')
        break



print('finished collecting urls')


df = pd.DataFrame(columns=['id', 'title', 'EC', 'url'])

#url = "https://clinicaltrials.gov/ct2/show/NCT02344550?cond=Metastatic+Breast+Cancer&cntry=KR&rank=1"
for url in urls:

    id_ = url[len("https://clinicaltrials.gov/ct2/show/"):]
    id_idx = id_.index("?")
    id_ = id_[:id_idx]

    driver.get(url)
    html = driver.page_source
    bs = BeautifulSoup(html, 'html.parser')

    title = bs.find_all("h1")[0].get_text()
    print(title.strip())


    ectext = bs.find_all("div", class_="indent2")
    #print(len(ectext))

    criteria = ""
    for t in ectext:
        if t.find(text=re.compile("Inclusion Criteria")):
            #print("=========================================")
            ts = str(t)
            idx = re.search("<p style=.+(I|i)nclusion (C|c)riteria", ts).start()
            ts2 = ts[idx:]
            idx = ts2.index("</div>")
            ts2 = ts2[:idx]
            final = re.compile(r'<.*?>')  # tags look like <...>

            criteria = final.sub('', ts2)
            break


    d = [id_, '\"'+title+'\"', criteria, url]

    df.loc[len(df)] = d

df.to_csv(res_file, index=True, encoding='utf-8')


print('saved file: '+res_file)
driver.quit()


import smtplib
import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

#This function sends an email notifying that the price on the specific sneakers is below 800 SEK
#If your email address is not gmail.com, then you have to change the SMTP (smtp.gmail.com) and port (465).
#A warning for those who have a gmail address: in order to send an email to your address, one needs to turn on the 2-step 
#verification and create an App Password (a 16-digit password which is used as 'your password' below). Although, Google 
#says that App Passwords aren’t recommended and are unnecessary in most cases as they are less safe. But this is the only
#way to make it work.
def send_email(sneakers_name: str):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465) 
    server.login('your email address', 'your password')
    subject = "Nike Dunk, price"
    body = 'Nike Dunk ' + sneakers_name + ' are now below 800 kr!'
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail('from email address', 'to email address', msg)


#This function opens Safari (if you're using another browser, then specify it below, webdriver.yourbrowser), scrapes all 
#information about Nike Dunk sneakers (brand, colourway, price and the date) and saves it in a .csv file. If such a file 
#already exists, it adds the new information to the file.
def check_price():
    driver = webdriver.Safari('location of your webdriver') #For me the location is '/usr/bin/safaridriver'
    url = 'https://www.zalando.se/herrskor/?q=nike+dunk' 
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    brand = driver.find_elements(By.XPATH, '//h3[@class="OBkCPz lystZ1 m3OCL3 HlZ_Tf ja2E95 IvrHht ZkIJC- u-kVXO"]')
    sneakers = driver.find_elements(By.XPATH, '//h3[@class="voFjEy lystZ1 m3OCL3 HlZ_Tf ja2E95 IvrHht ZkIJC- u-kVXO"]')
    price = driver.find_elements(By.XPATH, '//section[@class="_0xLoFW _78xIQ-"]')

    list = []
    for element in range(len(price)):
        price_new = re.findall(r'\d+', price[element].text)
        if len(price_new[0]) == 1:
            list.append([brand[element].text, sneakers[element].text.split('-')[0],
                         sneakers[element].text.split('-')[2], int(price_new[0] + price_new[1])])
        else:
            list.append([brand[element].text, sneakers[element].text.split('-')[0],
                         sneakers[element].text.split('-')[2], int(price_new[0])])
            if int(price_new[0]) < 800: #If price of some pair of sneakers has dropped below 800 SEK, then send an email
                send_email(sneakers[element].text.split('-')[2])

    header = ['Brand', 'Sneakers', 'Colourway', 'Price (SEK) on ' + str(datetime.datetime.now())[:19]]
    df = Path(r'path where Python stores your files and the name of the file') #For me: r'/Users/alex/PyCharmMiscProject/Nike_Dunk.csv'
    if df.is_file():
        df = pd.read_csv(r'/Users/alex/PyCharmMiscProject/Nike_Dunk.csv')
        df1 = pd.DataFrame(np.array(list), columns=header)
        df2 = df.merge(df1, on=['Brand', 'Sneakers', 'Colourway'], how='outer')
        df2.to_csv('Nike_Dunk.csv', index=False)
    else:
        df1 = pd.DataFrame(np.array(list), columns=header)
        df1.to_csv('Nike_Dunk.csv', index=False)

    driver.close()
    

#The statement below runs the function once a day 
while True:
    check_price()
    time.sleep(86400) #60 sec * 60 min * 24 h
    

#The function below plots a graph of how price on specific sneakers changes
def price_evolution(sneakers_number: int):
    df = Path(r'/Users/alex/PyCharmMiscProject/Nike_Dunk.csv')
    if df.is_file():
        df = pd.read_csv(r'/Users/alex/PyCharmMiscProject/Nike_Dunk.csv')
        if sneakers_number in range(len(df.iloc[:, sneakers_number])):
            try:
                fig, ax = plt.subplots()
                ax.plot(df.columns[3:].tolist(), df.transpose().iloc[3:, :][sneakers_number])
                plt.title('Change of price of Nike Dunk' + df.transpose().iloc[2,:][sneakers_number] + '\n from ' +
                      df.columns[3:].tolist()[0][15:25] + ' to ' + df.columns[3:].tolist()[-1][15:25])
                plt.xlabel('Date')
                ax.set_xticks(ax.get_xticks())
                ax.set_xticklabels(labels=[x[15:25] for x in df.columns[3:].tolist()], rotation=45)
                plt.ylabel('Price (SEK)')
                plt.grid(linestyle = '--', linewidth = 0.5)
                plt.show()
            except:
                print('The data does not exist')
        else:
            print('The number of the sneakers should be in range ' + str(len(df.iloc[:, -1])))

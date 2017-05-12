from bs4 import BeautifulSoup
import requests
import numpy as np
import csv
import re 
import time
import smtplib
import time

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

reader = csv.reader(open("urls.csv", "r"), delimiter=",") #store the information you want in a csv
data = list(reader)
while True: #forever    
    prices = np.zeros(len(data)-1)

    for i,el in enumerate(data):
        if i==0:
	    continue
	title = el[0]
	author = el[1]
	url_to_scrape = el[2]
	tmp = []
	r = requests.get(url_to_scrape)	  #grab the html
	soup = BeautifulSoup(r.text, 'html.parser')
        
        #read prices from that file
	for price in soup.select(".text-left, .price label"): #text extraction for prices, these tags are imperfect but serve as a fair guess
	    price = price.text
	    price = re.findall("\d+\.\d+", price)
	    if len(price) > 0: 
	        if is_number(price[0]):
		    tmp.append(float(price[0]))



	if len(tmp) > 1:
		tmp = np.sort(tmp)[1:] #get lowest price, but the first is usually not correct
	best_price = tmp[0]

	prices[i-1] = best_price # store it for laters

	#print("Title: %s \t Author: %s \t Lowest Price atm: %.2f\n"%(title,author,best_price))

    old_prices = np.loadtxt("old_prices.csv",delimiter=",")
    if old_prices.shape[1] != len(prices): #a new link was added to the spreadsheet
        new_old_prices = np.zeros((old_prices.shape[0],len(prices)))
        for i,el in enumerate(old_prices):
            new_old_prices[i] = np.append(el,[0],0)
        old_prices = new_old_prices 

    avg = np.mean(old_prices,0)
    ab_check = prices < (avg * .95) #if less than 95 percent of past N price checks, alert
    abnormal = False
    inds_ab = []
    if np.sum(ab_check) > 0:
        for i,el in enumerate(ab_check):
            if (el == True) & (prices[i] != old_prices[-1][i]): #make sure the prices actually changed from last time
                abnormal == True
                inds_ab.append(i)
    old_prices = np.append([prices],old_prices,0) #append the new prices to the array
    while old_prices.shape[0] > 10: #only keep last 10
        old_prices = np.delete(old_prices,10,0)
    np.savetxt("old_prices.csv",old_prices,fmt="%.2f",delimiter=',')
    
    #if they are abnormal, send email
    if abnormal == True:
        msg = "A textbook price or two recently dipped, info below\n\n"
        for i in range(np.sum(ab_check)): #for each book displayin abnormal behavior
            author_ab = data[inds_ab[i]+1][1]
            title_ab = data[inds_ab[i]+1][0]
            price_norm = avg[inds_ab[i]]
            price_ab = prices[inds_ab[i]]
            url_ab = data[inds_ab[i]+1][2]

            msg += "Author: %s \n Title: %s \n URL: %s \n Normal Price: %.2f\n Abnormal Price: %.2f\n\n"%(author_ab,title_ab,url_ab, price_norm,price_ab)

        to_email = "tomkoch96@yahoo.com"
        from_email = "verdusatest@gmail.com"
        usn = from_email
        pw = "happycrayon"

        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(usn,pw)
        server.sendmail(from_email, to_email, msg)
        server.close()
    f=open('all_prices.csv','a')
    np.savetxt(f,[prices],fmt='%.2f')
    f.close()
    time.sleep(600)


from bs4 import BeautifulSoup
import requests
import numpy as np
import csv
import re 
import time
import smtp

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

reader = csv.reader(open("urls.csv", "r"), delimiter=",") #store the information you want in a csv
data = list(reader)
prices = np.zeros(len(data))
print("Finding the lowest prices according to cheapesttextbooks.com. If you see a price that seems unrealistic, it probably is.\n\n\n")

for i,el in enumerate(data):
	if i==0:
		continue
	title = el[0]
	author = el[1]
	url_to_scrape = el[2]
	tmp = []
	r = requests.get(url_to_scrape)	  #grab the html
	soup = BeautifulSoup(r.text, 'html.parser')
	 
	for price in soup.select(".text-left, .price label"): #text extraction for prices, these tags are imperfect but serve as a fair guess
		price = price.text
		price = re.findall("\d+\.\d+", price)
		if len(price) > 0: 
			if is_number(price[0]):
				tmp.append(float(price[0]))



	if len(tmp) > 1:
		tmp = np.sort(tmp)[1:] #get lowest price, but the first is usually not correct
	best_price = tmp[0]

	prices[i] = best_price # store it for laters

	#print("Title: %s \t Author: %s \t Lowest Price atm: %.2f\n"%(title,author,best_price))
        
old_prices = np.loadtxt("old_prices.csv")
avg = np.mean(old_prices,0)
ab_check = prices < (avg * .95) #if less than 95 percent of past N price checks, alert
abnormal = False
if np.sum(ab_check) > 0:
    abnormal == True

np.append(old_prices,prices,0) #append the new prices to the array
while old_prices.shape[0] > 10: #only keep last 10
    np.delete(old_prices,9,0)
np.savetxt(old_prices,"old_prices.csv")

#if they are abnormal, send email
if abnormal == True:

    msg = "A textbook price or two recently dipped, info below\n\n"
    for i in range(sum(ab_check)): #for each book displayin abnormal behavior
        author_ab = data[i][1]
        title_ab = data[i][0]
        price_norm = avg[i]
        price_ab = prices[i]
        url_ab = data[i][2]

        msg += "Author: %s \n Title: %s \n URL: %s \n Normal Price \n Abnormal Price\n\n"%(author_ab,title_ab,url_ab, price_norm,price_ab)

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



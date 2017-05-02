from bs4 import BeautifulSoup
import requests
import numpy as np
import csv
import re 
import time

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
	tmp = np.sort(tmp)[1:] #get lowest price
	best_price = tmp[0]

	prices[i] = best_price # store it for laters

	print("Title: %s \t Author: %s \t Lowest Price atm: %.4f\n"%(title,author,best_price))

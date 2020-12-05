#!/usr/bin/env python3 

#Test Script to Scrape a Client Product Page for Azarella 
#Test Client: Tentree
#Test Page: Women's Joggers & Sweatpants 

#NOTES:
#Continuous Integration may be solid apporach to ensure scrapers still functional, despite sites changing 
#https://realpython.com/python-continuous-integration/

#Question for Drew and Alexa (and site owners?): Do any of your clients have API's for their sites? If unknonw, can you ask? Low chance small retail websites WILL but if do then will make a specific site far far easier to handle - instead of scraping site at its source, can use an API call to make life easier ie product = API.getProduct 

#Don't think will need anything scraped that is hidden behind a login page but if so (plus side note for me) there are ways to do this. Advanced techniques using the requests library to allow HTTP request from script. Look into if have time and interest 

#If site dynamic (prob) then will send JavaScript code to client to execute to create HTML rendering. For script this meqans that what the server sends me from my request will not be HTML but JavaScript code. Can use request-html to execute this code (can also use Selenium). Request-html allows capablity to execute code using BeautifulSoup under the hood 

from bs4 import BeautifulSoup 
import requests
import json
import csv 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#Website URL 
url = "https://www.tentree.com/collections/womens-pants/products/women-french-terry-jogger?METEORITE%20BLAC"
url1 = "https://www.tentree.com/collections/womens-pants/products/w-pacific-jogger-ev2?OLIVE%20NIGHT%20GREEN"
#Headers for system we are running this on 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHT    ML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#Input: A string containing URL, a string containing system headers
#Output: An array info, with product info
def get_product_info(url,headers,userPath):
	
	#Request Site Data 
	req = requests.get(url,headers=headers)
	
	#Get text of site 
	page = req.text
	
	#This creates a Beautiful Soup object that will parse all that structured HTML data 
	soup = BeautifulSoup(page,'html.parser')
	
	page_content = soup.find(id="pageContent")

	###############		PRODUCT BASICS: TITLE, SKU, PRICE	##################
	product_page = page_content.find("div",class_="product-page")	
	product_title = product_page.find("span",class_="title")
	product_sku = product_page.find("span",class_="sku")
	product_price = product_page.find("div",class_="price offset-10")
	product_review = product_page.find("div",class_="product__review")
	info = []
	info.append(product_title.text.strip())
	info.append(product_sku.text[6:].strip())
	info.append(product_price.text.strip())
	price = product_price.text.strip()
	
	#################	ECO-LOG VALUES: WATER, CO2, WASTE 	#################
	#Should only scrape for eco log values if can find it
	#This is necessary, as some tentree product pages were observed not having these 
	if product_page.find("div",class_="product__eco-log"):

		eco_log = product_page.find("div",class_="product__eco-log")
		eco_items = eco_log.find_all("div",class_="eco-log__item") 
		eco_values = eco_log.find_all("span",class_="eco-log__value")
		eco_properties = eco_log.find_all("span",class_="eco-log__property")
		
		temp = []
		eco = eco_log.text.strip().split("\n")
		for elm in eco:
			if elm == "":
				continue
			else:
				temp.append(elm)
		del temp[-1]
		i = 0 
		j = 1 
		while i < len(temp):
			info.append(temp[i].strip() + " " + temp[j].strip())
			i += 2 
			j += 2 

	################	PRODUCT DESCRIPTION 	#####################
	prod_des = product_page.find("div",class_="product-description")
	description = [] 
	for list_item in prod_des.find_all("li"):
		info.append(list_item.text.strip())

	###############		PRODUCT SIZES + COLORS 	####################
	description = product_page.find(id="tab-1")
	info.append(description.text.strip())
	
	driver = webdriver.Chrome(userPath)
	driver.get(url)
	color = driver.find_elements_by_xpath('//a[@class="swatch-color-ahref"]')
	colors = [] 
	for c in range(len(color)):
		colors.append(color[c].text.strip())
	info.append(colors)	
	
	size = driver.find_elements_by_xpath('//a[@class="is-available-true"]')
	sizes = [] 
	for s in range(len(size)):
		sizes.append(size[s].text.strip())
	info.append(sizes)
	return info 

#Input: A string containing topic page url, a string containing system headers
#Output: A CSV with all product page info logged 
def get_product_pages(url, headers):
	
	#Request Site Data 
	req = requests.get(url,headers=headers)

	#Get text of site 
	page = req.text
	
	#This creates a Beautiful Soup object that will parse all that structured HTML data 
	soup = BeautifulSoup(page,'html.parser')

	page_content = soup.find(id="pageContent")
	for link in page_content.find_all('a'):
		print(link)

	container = page_content.find(class_="br-container container-1440")
	grid = container.find(class_="grid gutter--flush")
	collection = grid.find(class_="collection-items")
	prod_list = collection.find('div',class_='product-listing row collection-products')
	
	for g in prod_list.find_all('div'):
		print(g)
	for prod in grid.find_all('div',class_='product'):
		print(prod)

	for col in collection.find_all('div',class_="col-xs-6 col-sm-6 col-md-4 col-lg-4 pr-grid"):
		link = col.find('a')
		print(link)

	for t in collection.find_all('p',class_="title"):
		print(t)
		print(t.find('href'))

	data = []
	#Get all product page links
	for link in collection.find_all('a'):
		temp = [] 
		#Scrape each link
		prod_url = link.get('href')
		print(prod_url)
		prod_url = "http://" + prod_url
		#print(prod_url)
		#temp = get_product_info(prod_url,headers)
		#Add page data to array 
		#data.append(temp)
	exit()
	#Write data array to a CSV 
	write_to_csv(data)



	
def write_to_csv(data):
	#NEED CSV TO BE IN UTF-8 ENCODING... CHECK INTERNET 
	with open('product_info.csv', mode='w', encoding="utf-8-sig") as csv_file:
		csv_writer = csv.writer(csv_file, delimiter=',')
		#Write each product info in one row at a time 
		temp = [] 
		for elm in data:
			csv_writer.writerow([elm])

def json_test(url,headers):

	
	#Request Site Data 
	req = requests.get(url,headers=headers)
	
	#Get text of site 
	page = req.text
	
	#This creates a Beautiful Soup object that will parse all that structured HTML data 
	soup = BeautifulSoup(page,"html.parser")
	script = soup.find_all("script")

	
	
	driver = webdriver.Chrome('/Users/CarterDuncan/Downloads/chromedriver')
	driver.get(url)
	json = driver.find_elements_by_xpath('//*[@id="pageContent"]/script[5]')
	for j in range(len(json)):
		print(j)


website = "https://www.tentree.com/collections/womens-pants" 
#get_product_pages(website,headers)


men_url = "https://www.tentree.com/collections/mens-hoodies/products/mens-outsider-classic-hoodie?HEATHER%20GREY"
kid_url = "https://www.tentree.com/collections/kids/products/kids-juniper-tshirt?METEORITE%20BLACK%20HEATHER"
w1_url = "https://www.tentree.com/collections/womens-t-shirts-tanks/products/no-pollution-unisex-t-shirt?JET%20BLACK"
m1_url = "https://www.tentree.com/collections/mens-shirts-button-ups/products/heavy-weight-flannel-shirt?RUBBER%20BROWN%20RETRO%20PLAID"
m2_url = "https://www.tentree.com/collections/mens-hoodies/products/mens-outsider-classic-hoodie?HEATHER%20GREY"
k1_url = "https://www.tentree.com/collections/kids/products/kids-emb-graphic-tshirt?PERISCOPE%20GREY%20HEATHER"

#print(get_product_info(w1_url,headers), "\n")
#print(get_product_info(m1_url,headers), "\n")
#print(get_product_info(m2_url,headers), "\n")
#print(get_product_info(k1_url,headers), "\n")

print("Please past the link to a product page now:")
user_url = input() 
print("Please enter the pathway to your chrome driver")
userPath = input() 
test = get_product_info(user_url,headers,userPath)
write_to_csv(test)


#json_test(men_url,headers)
#get_product_info(men_url,headers)


#MODIFY SO READ LIST OF LINKS OF PRODUCT PAGES 
#GETS ALL INFO FROM EACH PRODUCT LINK 
#UPLOADS ALL PRODUCT INFO INTO CSV


#IF GIVEN A LIST OF AFFILATE LINKS, APPEND EACH AFFILATE LINK TO END OF CSV PRODUCT ROW 





#TO MAKE CRAWLER MORE ROBUST USE:
#SCHEMA.ORG (Lots of websites will have a schema.org information on their site) 
#also refered to as microdata 

#JSONLD
#JSON LINKED DYNAMIC - JAVASCRIPT INTERNALS 
#THEN CRAWLER JUST PULLS MICRODATA FROM JSONLD

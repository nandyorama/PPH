import requests,os,bs4
import webbrowser
import sys
import json
import logging
import datetime
import time


fileName= "actor.json"
data = []
site = "http://a2zen.fm/podcast/inspired-choices-with-christine-mciver/"
actor = "/name/nm0759207/"

logging.basicConfig(filename="A2z.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def CreateUrl(actor):
	url = site
	logging.debug("\nReturning From CreateUrl"+url+"\n")
	return url

def GetSoup(url):
	logging.debug("\nStart GetSoup\n")
	res = requests.get(url)
	try:
		res.raise_for_status()
		soup = bs4.BeautifulSoup(res.text)
		return soup
	except requests.exceptions.HTTPError:
		print("Some Problem in GetSoup")
		logging.error("\nException From GetSoup Method\n")
		return " "

def GetRequest(soup,choice="NO"):
	logging.info("\n Start GetRequest\n")

	if choice == "Yes":
		comicElem = soup.select('#main .see-more')
		logging.info("\nRequest Using SEE-MORE in Main\n")
	else:
		comicElem = soup.select('div.single-media-wrap')# .media-description
		logging.info("\nRequest Using TITLE in Main\n")

	return comicElem

def Find(soup):
	Element = GetRequest(soup,"NO")
	print("Number of Element s present is "+str(len(Element)))
	logging.info(Element)
	actorDict={}
	try:
		for index in range(len(Element)):
			
			img = Element[index].select('.media-title meta_btn > a')
			print(str(img)+"?????")
			#temp = img.getText()
			#print("Title---"+temp)
			#actorDict["Title"]=temp
	
			des = Element[index].select('.description')
			print("Descrip----"+str((des[0].getText())))
			actorDict["Description"]=str(des[0].getText())
#	
#			#Birth = ""
			birth = Element[index].select('div.view-like .like_count')
			temp = birth[0].getText()
			print(str(temp)+"<<<<<<<<<<<<")			
			actorDict["Like"]=str(temp.encode('utf-8'))
#	
#			#Dep=[]
			dep = Element[index].select('div.view-like .views')
			print("Views----"+str((dep[0].getText()).encode('utf-8')))
			actorDict["View"]=str((dep[0].getText()).encode('utf-8'))
	except IndexError:
		print("Sthg Went Wrong")
	
	print("-------------")
	print(actorDict)
	#out_file = open("a2z.json","a")
	#json.dump(dict,out_file, indent=4)                               
	#out_file.close()


def Read():
	#print((data))
	url = CreateUrl(actor)
	soup = GetSoup(url)
	Find(soup)

if __name__=="__main__":
	Read()

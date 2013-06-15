from bs4 import BeautifulSoup
import urllib2
import json

BASE_URL = 'http://www.forbes.com/global2000/list/#page:{0}_sort:0_direction:asc_search:_filter:All%20industries_filter:All%20countries_filter:All%20states'
BASE_IMG_URL = 'http://i.forbesimg.com/media/lists/companies/{0}_{1}.jpg'
BASE_IMG_SIZE = ['50x50', '100x100', '150x150', '200x200', '300x300', '400x400']
BASE_PARENT_URL = 'http://www.forbes.com{0}'
companyPayload = []
imgLinkList = []
companyNameList = []
companyHTMLnameList = []
countryList = []
valuationList = []
companyInfo = {}  # Dictionary of company information which is primarily accessible by company html-friendly name
companyInfoIndexed = []  # List of company information which is primarily accessible by index number
maxPages = 20
imgPath = 'images/'
jsonPath = 'json/companyInfo.json'
jsonIndexedPath = 'json/companyInfoIndexed.json'

#companyInfo = {'name': companyNameList[], 'htmlName': companyHTMLnameList[], sales': sales, 'profits': profits, 'assets': assets, 'marketValue': marketValue}

# TODO: turn into a loop
try:
	data = urllib2.urlopen(BASE_URL.format(maxPages)).read()
except:
	print 'Error opening BASE_URL.Terminating Program.'

soup = BeautifulSoup(data)

# Extracts a chunk of HTML in which company names are located
htmlChunk = soup.find(id="listbody")
htmlCountryList = htmlChunk.find_all('td')
htmlValuationList = htmlChunk.find_all(class_='nowrap')

companyCount = 100 * maxPages

# GET VALUATION
j = 0
limit = len(htmlValuationList) / 4
for valuations in xrange(limit):
	sales = htmlValuationList[j].get_text()
	profits = htmlValuationList[j + 1].get_text()
	assets = htmlValuationList[j + 2].get_text()
	marketValuation = htmlValuationList[j + 3].get_text()
	valuationList.append({'sales': sales, 'profits': profits, 'assets': assets, 'marketValuation': marketValuation})
	j += 4

# GET COUNTRY
j = 0
limit = len(htmlCountryList) / 7
for i in xrange(limit):
	country = htmlCountryList[j + 2].get_text()
	countryList.append(country)
	j += 7

# EXTRACT HTML-FRIENDLY COMPANY NAMES (WITH DASHES) FROM HTMLCHUNK
for chunk in htmlChunk.find_all('a'):
	companyPath = chunk.get('href')
	endPos = companyPath.find('/', 12)
	name = companyPath[11:endPos]
	companyHTMLnameList.append(name)

# EXTRACT COMPANY NAMES IN PRINABLE UTF-8 FORMAT
companyNameList = [name.get_text().strip().replace(';', '') for name in htmlChunk.find_all('h3')]

for i in xrange(companyCount):
	# do stuff
	companyPayload.append(valuationList[i])
	companyPayload[i].update({'country': countryList[i]})
	companyPayload[i].update({'htmlName': companyHTMLnameList[i]})
	companyPayload[i].update({'name': companyNameList[i]})
	companyInfoIndexed.append(companyPayload[i])
for i in xrange(companyCount):
	companyInfo.update({companyHTMLnameList[i]: {}})
	companyInfo[companyHTMLnameList[i]].update({'country': countryList[i]})
	companyInfo[companyHTMLnameList[i]].update({'name': companyNameList[i]})
	companyInfo[companyHTMLnameList[i]].update(valuationList[i])

# write company info to json file (pickalable (near ascii) format)
j = json.dumps(companyInfo)
jIndexed = json.dumps(companyInfoIndexed)

with open(jsonPath, 'wb') as f:
	f.write(j)
with open(jsonIndexedPath, 'wb') as f:
	f.write(jIndexed)

# GET COMPANY LOGOS FROM FORBES.COM
print 'Fetching images...'
for companyName in companyHTMLnameList:
	for imgSize in BASE_IMG_SIZE:
		imgURL = BASE_IMG_URL.format(companyName, imgSize)
		imgFile = ''.join([companyName, '_', imgSize, '.jpg'])
		try:
			jpgfile = urllib2.urlopen(imgURL).read()
			with open(imgPath + imgFile, 'wb') as f:
				f.write(jpgfile)
				print 'Successfully downloaded {0}'.format(jpgfile)
		except:
			print 'Error downloading {0}'.format(imgFile)
			pass

# extract company info (name, htmlName, sales, profits, assets, marketValue, country) from htmlblock

# something to think about: Should the info below be acquired through current site or main company forbes page?
# (1) within id='listbody' > tr > td.nowrap: [sales, profits, assets, Marketval]
# (2) Option to obtain additional info: INDUSTRY, FOUNDING YEAR, CEO, WEBSITE, EMPLOYEE COUNT



print 'Forbes 2000 Coroporate Logo collection complete.'
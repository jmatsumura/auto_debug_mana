#!/usr/bin/python

# This is a modified version of the crawler/health_check scripts that runs
# headless via PhantomJS. This is to get around issues with dependency 
# updates with both Chrome and the Chrome driver. 

import sys, time
from selenium import webdriver

# Function to try find expected text within a page. Accepts the text 
# that is to be parsed. Must be careful using this function as it 
# searches for text on the CURRENT page. Thus, be meticulous about 
# which page is currently being viewed currently.  
def findInPage(text):

	result = 'SUCCESS'
	try:
		assert text in driver.page_source
	except:
		result = 'FAILURE' # if not in page, fail
	return result

# This function is used to check for all expected text on a 
# particular page. The input argument is a list of strings for
# what needs to be present on a particular page. 
def verify_results(listOfExpected): 
    result = 'SUCCESS'
    for x in listOfExpected:
        if listOfExpected.index(x) > 0: 
            if result != 'FAILURE':
                result = findInPage(x)
            else:
                break
        else:
            result = findInPage(x)
		
	return result


username 	=  str(sys.argv[1]) # let the user specify username
password 	=  str(sys.argv[2]) # let the user specify password
db		=  str(sys.argv[3]) # let the user specify db

driver = webdriver.PhantomJS()
driver.set_window_size(1100,900)
driver.set_window_position(0,0)
driver.get("https://manatee-preview.igs.umaryland.edu")

driver.find_element_by_name('user').send_keys(username)
driver.find_element_by_name('password').send_keys(password)
driver.find_element_by_name('db').send_keys(db)
driver.find_element_by_name('login_form').submit(), time.sleep(5)

expectedList = ["Access Annotation","Sequence Search",
			"Change Organism Database", "Data file downloads"]
result = verify_results(expectedList)
driver.quit()

if result == "SUCCESS":
    exit(0)

elif result == "FAILURE":
    exit(1)

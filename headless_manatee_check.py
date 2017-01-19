#!/usr/bin/python

# This is a modified version of the crawler/health_check scripts that runs
# headless via PhantomJS. This is to get around issues with dependency 
# updates with both Chrome and the Chrome driver. 

import sys, time
from selenium import webdriver

def main():

    username s=  str(sys.argv[1]) # let the user specify username
    password =  str(sys.argv[2]) # let the user specify password
    db	=  str(sys.argv[3]) # let the user specify db

    driver = webdriver.PhantomJS(r'/usr/bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    driver.set_window_size(1100,900)
    driver.set_window_position(0,0)
    driver.get("https://manatee-staging.igs.umaryland.edu")

######## Check that login is correct
    userBox = driver.find_element_by_name('user')
    pwBox = driver.find_element_by_name('password')
    dbBox = driver.find_element_by_name('db')
    loginForm = driver.find_element_by_name('login_form')
    userBox.send_keys(username)
    pwBox.send_keys(password)
    dbBox.send_keys(db)
    loginForm.submit(), time.sleep(5)

    expectedList = ["Access Annotation","Sequence Search",
                "Change Organism Database", "Data file downloads"]
    result = verify_results(expectedList)

##########################################
##### TESTING SUITE = ann_tools.cgi ######
##########################################
	driver.find_element_by_partial_link_text("Search/Browse").click(), time.sleep(5)

######## Check that coord search is correct
	currentCGI = 'coordinate_view.cgi'
	end5 = driver.find_element_by_name('end5')
	end3 = driver.find_element_by_name('end3')
	end5.send_keys("1000")
	end3.send_keys("5000")
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(12)
	expectedList = ["VAC.pseudomolecule.1","VAC_4","VAC_5","VAC_6","gene name",
			"UDP-glucose 6-dehydrogenase","VAC_3","2746","1.1.1.44"]
	result = verify_results(expectedList)	
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click(), time.sleep(5)

    driver.quit() 

##########################################
######## TESTING SUITE = dumpers #########
##########################################


######### Coords
	#driver.find_element_by_partial_link_text('Gene Coordinates').click(), time.sleep(60)
	#result = compare_dl_files('coord.txt')
	#log_results(currentCGI, result, fileName, 'Coords dumper')
	#driver.find_element_by_partial_link_text("Home").click() 
    #driver.quit()


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

    if result == 'SUCCESS':
        exit(0)
    elif result == 'FAILURE':
        exit(1)

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


if __name__ == '__main__':
	main()
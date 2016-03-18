#!/usr/bin/python

# The purpose of this script is to simulate all the possible actions that a user 
# could perform throughout a normal interaction with Manatee. The idea is that 
# the script will fill in forms and submit specific values that lead to a known
# result. These actions will be verified for correctness and the script will 
# cease at a page which doesn't yield the expected results (if one is found).
# All results will be written to a file in the /tmp/ directory which 
# communicates which *.cgi were checked and whether or not they are OK.   
#
# Note that the tests will be performed in order of navigation throughout 
# Manatee, not just going to each page individually. Meaning, login.cgi 
# is checked first, then gateway.cgi, then all the other tools going to and
# from gateway.cgi, etc. This is to properly emulate the actions that a user 
# would perform. Manatee seems to die unnaturally sometimes (so one error
# may inhibit the ability to even go back to the 'Home' page), thus, the 
# log file will die somewhat arbitrarily at whatever script fails as to not
# mislead where the problem actually is rooted. Comments within the main
# body that start at the left end of the page with hashmarks detail a
# specific component of the page that is being tested.  
#
# HOWTO: (python) first.py http://path/to/manatee/site/login
#
# Author: James Matsumura

import time, string, random, sys
from selenium import webdriver

# Generate a new log filename with a random ID
fileName = '/tmp/manateeAutoDebug.' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) 

pathToManatee 	=  str(sys.argv[1]) # let the user specify which server to test
username 	=  str(sys.argv[2]) # let the user specify username
password 	=  str(sys.argv[3]) # let the user specify password
db		=  str(sys.argv[4]) # let the user specify db
driver = webdriver.Chrome()  # Optional argument to find chromedriver install

def main():

	##########################################
	######## TESTING PAGE = login.cgi ########
	##########################################

	currentCGI = 'login.cgi'

	driver.get(pathToManatee)

	expectedList = ["user_name","password","database"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')

######### Test the form
	userBox = driver.find_element_by_name('user')
	pwBox = driver.find_element_by_name('password')
	dbBox = driver.find_element_by_name('db')
	loginForm = driver.find_element_by_name('login_form') # note that forms need to be reassigned every new page visit
	userBox.send_keys(username)
	pwBox.send_keys(password)
	dbBox.send_keys(db)
	loginForm.submit()
	time.sleep(5) # wait for gateway to load

######### Test that the login successfully went through. 
	expectedList = ["ACCESS LISTINGS","ACCESS GENE CURATION PAGE",
			"CHANGE ORGANISM DATABASE", "Data file downloads"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'submit')
	time.sleep(2)

	##########################################
	####### TESTING PAGE = gateway.cgi #######
	##########################################
	# As gateway links to numerous pages, many testing pages will fall under this umbrella

######### Go to Search/Browse
	currentCGI = 'ann_tools.cgi'
	driver.find_element_by_partial_link_text("Search/Browse").click() 
	expectedList = ["ACCESS GENE LISTS","select coordinate range:","ROLE CATEGORY BREAKDOWN",
			"SEARCH GENES BY"]
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Genome Viewer
	currentCGI = 'genome_viewer.cgi'
	driver.find_element_by_partial_link_text("Genome Viewer").click() 
	expectedList = ["Find Orf","Coord Search"]
	time.sleep(20)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.back() # currently, genome viewer has no home link

######### Go to Genome Statistics
	currentCGI = 'summary_page.cgi'
	driver.find_element_by_partial_link_text("Genome Statistics").click() 
	expectedList = ["24.8%","25.7%","24.9%","24.6%","Genome Summary",
			"5204","88","13","4462","5245125 bp"]
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Role Category Breakdown
	currentCGI = 'roleid_breakdown.cgi'
	driver.find_element_by_partial_link_text("Role Category Breakdown").click() 
	expectedList = ["69.7","15.2","4.0","0.0","7.8", "0.7",
			"Role category not yet assigned","407",
			"Hypothetical proteins","828"]
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Overlap summary
	currentCGI = 'overlap_summary.cgi'
	driver.find_element_by_partial_link_text("Overlap Summary").click() 
	expectedList = ["VAC_148","170895","171202","44 nucleotides","VAC_150","171040","171202",
			"VAC_5210","5173634","5174493","35 nucleotides","VAC_5211","5174340","5174493"]
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Test going to GCP
	currentCGI = 'ORF_infopage.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_241')
	gatewayForm.submit()
	expectedList = ["VAC_241","end5/end3:","550","undecaprenyl phosphate","GO:0016763","Cellular processes",
			"Start confidence not calculated","Frameshift Name","EVIDENCE PICTURE","PF02366.13",
			"COG1807","No prosite data available","0.209","0.365","CHARACTERIZED MATCH","UniRef100_B1X8X0"]
	time.sleep(10)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Test changing db
	currentCGI = 'gateway.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('abau')
	gatewayForm.submit()
	expectedList = ["Acinetobacter baumannii ATCC 17978"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'change db')
	time.sleep(2)

######### Revert to test db
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC_test')
	gatewayForm.submit()
	expectedList = ["Escherichia coli VAC1"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'change db back')

######### DONE
	time.sleep(10) # hang a bit before the end
	driver.quit()

###################################
#########   FUNCTIONS   ###########
###################################

# Function to log the results. Takes in the name of the script
# being assessed, the result found for the script, the path
# to the file being written to /tmp/ for output, and an
# a brief description of what aspect of the script is being 
# tested. For instance, on the gateway.cgi page there are 
# many different options to providing a brief description of
# the current test helps communicate which part of it failed. 
def log_results(script, result, pathToFile, desc):

	f = open(pathToFile, 'a+')
	f.write("%s\t\t\t%s\t\t\t%s\n" % (script, desc, result))

	if result == 'FAILED': sys.exit() # end everything at first failure

# Function that uses selenium to try find expected text within
# a page. Accepts the text that is to be parsed. Must be careful
# using this function as it searches for text on the CURRENT 
# page. Thus, be meticulous about which page is currently being 
# viewed and document it throughout the code.  
def findInPage(text):

	result = 'OK'
	try:
		assert text in driver.page_source
	except:
		result = 'FAILED' # if not in page, fail
	return result

# This function is used to check for all expected text on a 
# particular page. The input argument is a list of strings for
# what needs to be present on a particular page. 
def verify_results(listOfExpected): 

	result = ''
	for x in listOfExpected:
		if listOfExpected.index(x) > 0: 
			if result != 'FAILED': result = findInPage(x)
		elif result == 'FAILED': break 
		else: result = findInPage(x) 
		
	return result

if __name__ == '__main__':
	main()

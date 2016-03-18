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

b='BEFORE' # These two lines are used for log_results function, they are
a='AFTER'  # declared for the sake of simplicity

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

	# Test that the proper login page is displayed. 
	#result = findInPage("user_name")
	#if result != 'FAILED': result = findInPage("password")
	#if result != 'FAILED': result = findInPage("database")
	expectedList = ["user_name","password","database"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, b)

######### Test the form
	userBox = driver.find_element_by_name('user')
	pwBox = driver.find_element_by_name('password')
	dbBox = driver.find_element_by_name('db')
	loginForm = driver.find_element_by_name('login_form')
	userBox.send_keys(username)
	pwBox.send_keys(password)
	dbBox.send_keys(db)
	loginForm.submit()
	time.sleep(8) # wait for gateway to load

######### Test that the login successfully went through. 
	expectedList = ["ACCESS LISTINGS"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, a)

	##########################################
	####### TESTING PAGE = gateway.cgi #######
	##########################################
	result = ''
	currentCGI = 'gateway.cgi'

	#log_results(currentCGI, 'FAILED', fileName)
	driver.quit()

###################################
#########   FUNCTIONS   ###########
###################################

# Function to log the results. Takes in the name of the script
# being assessed, the result found for the script, the path
# to the file being written to /tmp/ for output, and an
# option for which page is being tested. Since on Manatee
# many pages require submissions, pass the 'b' parameter
# (Before submit) if testing the current page or 'a' parameter
# (After submit) if testing the page that appears after a form
# submission is performed. 
def log_results(script, result, pathToFile, o):

	f = open(pathToFile, 'a+')
	f.write("%s\t\t%s\t\t%s\n" % (script, o, result))

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

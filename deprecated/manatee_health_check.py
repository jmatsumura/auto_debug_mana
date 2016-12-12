#!/usr/bin/python

# The purpose of this script is to do a quick check for whether or not Manatee is functional. 
# This means testing image generation as well as whether or not the Manatee message consumer
# is working on Cruella. 
#
# HOWTO: (python) manatee_crawler.py http://path/to/manatee/site/login username password db
# The standard version of this script is verifying data within the db VAC_test.
#
# Author: James Matsumura

import time, string, random, sys, filecmp, glob, os, subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# Generate a new log filename with a random ID
fileName = '/tmp/manateeAutoDebug.' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) 

pathToManatee 	=  str(sys.argv[1]) # let the user specify which server to test
username 	=  str(sys.argv[2]) # let the user specify username
password 	=  str(sys.argv[3]) # let the user specify password
db		=  str(sys.argv[4]) # let the user specify db
driver = webdriver.Chrome() 

def main():

##########################################
######## TESTING PAGE = login.cgi ########
##########################################

	currentCGI = 'login.cgi'

	driver.get(pathToManatee)

	driver.set_window_position(0,0)
	driver.set_window_size(1100,900)

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
	loginForm.submit(), time.sleep(5) # using time.sleep is not optimal, but works best for Manatee's setup
	
######### Test that the login successfully went through. 
	expectedList = ["Access Annotation","Sequence Search",
			"Change Organism Database", "Data File Downloads"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'submit'), time.sleep(2)

######### Go to Genome Viewer
	currentCGI = 'genome_viewer.cgi'
	old_window = driver.window_handles[0]
	driver.find_element_by_partial_link_text("Genome Viewer").click(), time.sleep(5)
	new_window = driver.window_handles[1]
	driver.switch_to_window(new_window)
	expectedList = ["Find Orf","Coord Search"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.close()
	driver.switch_to_window(old_window)

######### Run BLASTP
	gatewayForm = driver.find_element_by_name('form1')
	driver.find_element_by_css_selector("#blastp").click()
	blastInputBox = driver.find_element_by_name('seq')
	blastInputBox.send_keys(''
		'VGLMWGLFSVIIASAAQLSLGFAASHLPPMTHLWDFIAALLAFGLDARILLLGLLGYLLS'
		'VFCWYKTLHKLALSKAYALLSMSYVLVWIASMVLPGWEGTFSLKALLGVACIMSGLMLIF'
		'LPTTKQRY'
				'')
	time.sleep(4)
	gatewayForm.submit(), time.sleep(10) # let BLAST run
	expectedList = ["(128 letters)","VAC_244","192","6e-51","VAC_3061",
			"1,139,576","(22.7 bits)","Effective search space: 61537104"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'BLASTP')
	driver.find_element_by_partial_link_text("Home").click() 

######### Change to db for dumper testing
	# This DB is different than the previous since the previous is subject to insertions,
	# deletions, and other modifications which may mislead the comparison of the data dumps
	# to their initial reference result.
	currentCGI = 'gateway.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC1_test2')
	gatewayForm.submit(), time.sleep(2)

	##########################################
	########## TESTING FN = DUMPERS ##########
	##########################################

	# Overestimate dumper time to ensure it completes
	# Find the most recent DL of this particular file and compare to reference

	pathToDataDumps = './VAC1_test2'
		
######### Coords
	driver.find_element_by_partial_link_text('Gene Coordinates').click(), time.sleep(60)
	result = compare_dl_files('coord.txt')
	log_results(currentCGI, result, fileName, 'Coords dumper')
	driver.find_element_by_partial_link_text("Home").click() 

############################
########## DONE ############
############################
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
	f.write("%s\t%s\t%s\n" % (script, desc, result))

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

# Function to ensure that particular text is not in a page.
def notFoundInPage(text):
	
	result = 'OK'
	try:
		assert text not in driver.page_source
	except:
		result = 'FAILED' # if found in page, fail
	return result

# Function to check that proper elements are appearing in Genome Viewer.
def gvCheck(text):
	
	result = 'OK'
	try:
		driver.find_element_by_css_selector(text)
	except NoSuchElementException:
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
		elif result == 'FAILED':  
			driver.quit()
			break
		else: result = findInPage(x) 
		
	return result

# This function is used to compare the current dumper output with
# that of a reference. This will search for the most recently 
# created file with the relevant suffix and run a diff of the two.
def compare_dl_files(fileExtension):

	# Need to handle gbk in a unique manner as the date will always modify the file slightly so a diff will return false
	if fileExtension == 'gbk':
		newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2.annotation.*.'+fileExtension), key=os.path.getctime)
		my_cmd = ['diff', '/Users/jmatsumura/mana_dumps/VAC1_test2.annotation.20160329.gbk'] + [newestFile]
		with open('/Users/jmatsumura/mana_dumps/gbk_diff.txt', "w") as outfile:
			subprocess.call(my_cmd, stdout=outfile)
		result = "OK" if os.stat("/Users/jmatsumura/mana_dumps/gbk_diff.txt").st_size < 300 else "FAILED"

	# Similar to the previous, handle by file size differences. 
	elif fileExtension == 'GO_annotation.txt':
		newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2_'+fileExtension), key=os.path.getctime)
		my_cmd = ['diff', '/Users/jmatsumura/mana_dumps/VAC1_test2_GO_annotation.txt'] + [newestFile]
		with open('/Users/jmatsumura/mana_dumps/GO_diff.txt', "w") as outfile:
			subprocess.call(my_cmd, stdout=outfile)
		f_size = os.stat("/Users/jmatsumura/mana_dumps/GO_diff.txt").st_size
		result = "OK" if ((f_size > 2200000) and (f_size < 2900000)) else "FAILED"

	elif fileExtension == 'tbl' or fileExtension == 'gff3':
		newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2.annotation.*.'+fileExtension), key=os.path.getctime)
		result = "OK" if filecmp.cmp('/Users/jmatsumura/mana_dumps/VAC1_test2.annotation.20160329.'+fileExtension, newestFile) else "FAILED"

	elif fileExtension == 'sigp':
		newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/sigp4.1_VAC.transcript.9803630972.1_pred.txt'), key=os.path.getctime)
		result = "OK" if filecmp.cmp('/Users/jmatsumura/mana_dumps/sigpOut.txt', newestFile) else "FAILED"

	else:
		newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2_'+fileExtension), key=os.path.getctime)
		result = "OK" if filecmp.cmp('/Users/jmatsumura/mana_dumps/VAC1_test2_'+fileExtension, newestFile) else "FAILED"

	return result 

if __name__ == '__main__':
	main()

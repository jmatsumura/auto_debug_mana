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
# HOWTO: (python) first.py http://path/to/manatee/site/login username password db
#
# Author: James Matsumura

import time, string, random, sys, filecmp, glob, os
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
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.back() # currently, genome viewer has no home link

######### Go to Genome Statistics
	currentCGI = 'summary_page.cgi'
	driver.find_element_by_partial_link_text("Genome Statistics").click() 
	expectedList = ["24.8%","25.7%","24.9%","24.6%","Genome Summary",
			"1100","tRNA","5245125 bp"]
	time.sleep(5)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Role Category Breakdown
	currentCGI = 'roleid_breakdown.cgi'
	driver.find_element_by_partial_link_text("Role Category Breakdown").click() 
	expectedList = ["703","Transposon functions","Chemotaxis and motility",
			"Role category not yet assigned","Chlorophyll",
			"Hypothetical proteins","94"]
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
	time.sleep(5)
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
	time.sleep(2)

######### Run BLASTN
	currentCGI = 'perform_blast.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	driver.find_element_by_css_selector("#blastn").click()
	blastInputBox = driver.find_element_by_name('seq')
	blastInputBox.send_keys(''
		'ATGAAATCGGTACGTTACCTTATCGGCCTCTTCGCATTTATTGCCTGCTATTACCTGTTA'
		'CCGATCAGCACGCGTCTGCTCTGGCAACCAGATGAAACGCGTTATGCGGAAATCAGTCGG'
		'GAAATGCTGGCATCCGGCGACTGGATTGTTCCCCATCTGTTAGGGCTACGTTATTTCGAA'
		'AAACCCATTGCCGGATACTGGATTAACAGCATTGGGCAATGGCTATTTGGCGCGAATAAC'
		'TTTGGTGTGCGGGCAGGCGTTATCTTTGCGACCCTGTTAACTGCCGCGCTGGTGACCTGG'
		'TTTACTCTGCGCTTATGGCGCGATAAACGTCTGGCTTTACTCGCCACAGTAATTTATCTC'
		'TCATTGTTTATTGTCTATGCCATCGGCACTTATGCCGTGCTCGATCCGTTTATTGCCTTC'
		'TGGCTGGTGGCGGGAATGTGCAGCTTCTGGCTGGCAATGCAGGCACAGACGTGGAAAGGC'
		'AAAAGCGCAGGATTTTTACTGCTGGGAATCACCTGCGGCATGGGGGTGATGACCAAAGGT'
		'TTTCTCGCCCTTGCCGTGCCGGTATTAAGCGTGCTGCCATGGGTAGCAACGCAAAAACGC'
		'TGGAAAGATCTCTTTATTTACGGCTGGCTGGCGGTTATCAGTTGCGTACTGACGGTTCTC'
		'CCCTGGGGACTGGCGATAGCGCAGCGGGAGCCTGACTTCTGGCATTATTTTTTCTGGGTT'
				'')
	time.sleep(4)
	gatewayForm.submit()
	expectedList = ["(720 letters)","VAC_241","1427","VAC_2870","VAC_1732",
			"4,590,078","(28.2 bits)","Effective search space: 3172774528"]
	time.sleep(10) # let the BLASTN run
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'BLASTN')
	driver.find_element_by_partial_link_text("Home").click() 

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
	gatewayForm.submit()
	expectedList = ["(128 letters)","VAC_244","192","6e-51","VAC_3061",
			"1,139,576","(22.7 bits)","Effective search space: 61537104"]
	time.sleep(10) # let BLAST run
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'BLASTP')
	driver.find_element_by_partial_link_text("Home").click() 

######### Run TBLASTN
	gatewayForm = driver.find_element_by_name('form1')
	driver.find_element_by_css_selector("#tblastn").click()
	blastInputBox = driver.find_element_by_name('seq')
	blastInputBox.send_keys(''
		'MIFSDWPWRHWRQVRGEAIALRLNDEQLNWRELCARVDELASSFAVQGVVEGSGVMLRAW'
		'NTPQTLLAWLALLQCGARVLPVNPQLPQPLLEELLPNLTLQFALVPEGENTFPALASLHI'
		'QLVEGAHAAAWQPTRLCSMTLTSGSTGLPKAAVHTYQAHLASAEGVLSLIPFGDHDDWLL'
		'SLPLFHVSGQGIMWRWLYAGARMTVRDKQPLEQMLAGCTHASLVPTQLWRLLVNRSSVSL'
		'KAVLLGGAAIPVELTEQAREQGIRCFCGYGLTEFASTVCAKEADGLADVGSPLPGREVKI'
		'VNDEVWLRAASMAEGYWRNGQRVPLVNDEGWYATRDRGEMHNGKLTIVGRLDNLFFSGGE'
		'GIQPEEVERVIAAHPAVLQVFIVPVADKEFGHRPVAVVEYDQQSVDLDEWVKDKLARFQQ'
		'PVRWLTLPPELKNGGIKISRQALKEWVQRQQ'
				'')
	time.sleep(4)
	gatewayForm.submit()
	expectedList = ["(451 letters)","VAC.pseudomolecule.1","866","0.0",
			"1,748,284","(26.2 bits)","Effective search space: 629382240"]
	time.sleep(10) # let BLAST run
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'TBLASTN')
	driver.find_element_by_partial_link_text("Home").click() 

######### Change to db for dumper testing
	# This DB is different than the previous since the previous is subject to insertions,
	# deletions, and other modifications which may mislead the comparison of the data dumps
	# to their initial reference result.
	currentCGI = 'gateway.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC1_test2')
	gatewayForm.submit()
	time.sleep(2)

	##########################################
	########## TESTING FN = DUMPERS ##########
	##########################################

	pathToDataDumps = '/Users/jmatsumura/Downloads/VAC1_test2'
		
######### GO Annotation
	currentCGI = 'nucleotide_dumper.cgi'
	driver.find_element_by_partial_link_text('GO Annotation').click() 
	time.sleep(180) # Overestimate dumper time to ensure it completes

	# Find the most recent dl of this particular file and compare to reference
	result = compare_dl_files('GO_annotation.txt')
	log_results(currentCGI, result, fileName, 'GO dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Annotation
	driver.find_element_by_partial_link_text('Annotation').click() 
	time.sleep(120) 
	result = compare_dl_files('annotation.txt')
	log_results(currentCGI, result, fileName, 'Annotation dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Coords
	driver.find_element_by_partial_link_text('Gene Coordinates').click() 
	time.sleep(40) 
	result = compare_dl_files('coord.txt')
	log_results(currentCGI, result, fileName, 'Coords dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Nucleotides
	driver.find_element_by_partial_link_text('Gene Nucleotide Sequence').click() 
	time.sleep(40) 
	result = compare_dl_files('nucleotide_multifasta_seq.fsa')
	log_results(currentCGI, result, fileName, 'Nucleotide dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Protein seqs
	driver.find_element_by_partial_link_text('Protein Sequence').click() 
	time.sleep(40) 
	result = compare_dl_files('protein_multifasta_seq.fsa')
	log_results(currentCGI, result, fileName, 'Protein dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Whole Genome
	driver.find_element_by_partial_link_text('Whole Genome Nucleotide Sequence').click() 
	time.sleep(40) 
	result = compare_dl_files('whole_genome.txt')
	log_results(currentCGI, result, fileName, 'Whole genome')
	driver.find_element_by_partial_link_text("Home").click() 

# These last 3 use a different script and have a different out format. 
######### GenBank
	driver.find_element_by_partial_link_text('GenBank Format').click() 
	time.sleep(120) 
	result = compare_dl_files_type_2('gbk')
	log_results(currentCGI, result, fileName, 'GenBank')
	driver.find_element_by_partial_link_text("Home").click() 

######### GFF3
	driver.find_element_by_partial_link_text('GFF3 Format').click() 
	time.sleep(120) 
	result = compare_dl_files_type_2('gff3')
	log_results(currentCGI, result, fileName, 'GFF3')
	driver.find_element_by_partial_link_text("Home").click() 

######### TBL
	driver.find_element_by_partial_link_text('TBL Format').click() 
	time.sleep(120) 
	result = compare_dl_files_type_2('tbl')
	log_results(currentCGI, result, fileName, 'TBL')
	driver.find_element_by_partial_link_text("Home").click() 

##########################################
#### TESTING PAGE = ORF_infopage.cgi #####
##########################################
# Already know GCP works, renavigate to same page. 

	currentCGI = 'gateway.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC_test')
	gatewayForm.submit()
	time.sleep(2)

	currentCGI = 'ORF_infopage.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_241')
	gatewayForm.submit()
	time.sleep(5)

	##########################################
	#### TESTING PAGE = btab_display.cgi #####
	##########################################

	currentCGI = 'btab_display.cgi'
	driver.find_element_by_partial_link_text('View BER Searches').click() 
	time.sleep(5) # let page load
	expectedList = ["UniRef100_B1X8X0","UniRef100_D7ZXT5","VAC.transcript.9703630972.1" 
			"VAC.CDS.980363074.1","%Identity = 98.7","%Similarity = 99.5"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'BER Searches Display')

	driver.find_element_by_partial_link_text('UniRef100_B1X8X0').click() 
	time.sleep(4)
	expectedList = ["Undecaprenyl phosphate-alpha-amino-4-deoxy-L-arabinose arabinosyl transferase", 
			"UniProt","UniRef100_B1X8X0"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'UniProt/UniRef')
	# New tab opened for UniProt, must close go back to BER display
	driver.send_keys(Keys.COMMAND + 'w')
	# New tab opened for BER display, must go back to GCP
	driver.send_keys(Keys.COMMAND + 'w')

############################
########## DONE ############
############################
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

# These two functions are used to compare the current dumper output with
# that of a reference. This will search for the most recently 
# created file with the relevant suffix and run a diff of the two.
def compare_dl_files(fileExtension):

	newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2_'+fileExtension), key=os.path.getctime)
	result = "OK" if filecmp.cmp('/Users/jmatsumura/mana_dumps/VAC1_test2_'+fileExtension, newestFile) else "FAILED"

	return result 

def compare_dl_files_type2(fileExtension):

	# Be sure to account for any date that may be attached.
	newestFile = min(glob.iglob('/Users/jmatsumura/Downloads/VAC1_test2.annotation.*.'+fileExtension), key=os.path.getctime)
	result = "OK" if filecmp.cmp('/Users/jmatsumura/mana_dumps/VAC1_test2.annotation.20160329.'+fileExtension, newestFile) else "FAILED"

	return result 

if __name__ == '__main__':
	main()

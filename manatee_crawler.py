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
# The standard version of this script is verifying data within the db VAC_test.
#
# Author: James Matsumura

import time, string, random, sys, filecmp, glob, os, subprocess
from random import randint
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
	expectedList = ["ACCESS LISTINGS","ACCESS GENE CURATION PAGE",
			"CHANGE ORGANISM DATABASE", "Data file downloads"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'submit'), time.sleep(2)

##########################################
###### TESTING SUITE = gateway.cgi #######
##########################################
# As gateway links to numerous pages, many testing pages will fall under this umbrella

######### Go to Search/Browse
	currentCGI = 'ann_tools.cgi'
	driver.find_element_by_partial_link_text("Search/Browse").click(), time.sleep(5)
	expectedList = ["ACCESS GENE LISTS","select coordinate range:","ROLE CATEGORY BREAKDOWN",
			"SEARCH GENES BY"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Genome Viewer
	currentCGI = 'genome_viewer.cgi'
	driver.find_element_by_partial_link_text("Genome Viewer").click(), time.sleep(5)
	expectedList = ["Find Orf","Coord Search"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.back() # currently, genome viewer has no home link

######### Go to Genome Statistics
	currentCGI = 'summary_page.cgi'
	driver.find_element_by_partial_link_text("Genome Statistics").click(), time.sleep(5)
	expectedList = ["24.8%","25.7%","24.9%","24.6%","Genome Summary",
			"1100","tRNA","5245125 bp"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')

######### Go to RNA display page
	currentCGI = 'display_feature.cgi'
	driver.find_element_by_partial_link_text('tRNA').click(), time.sleep(5)
	expectedList = ["VAC_171","VAC_5307","tRNA-Pro","VAC.pseudomolecule.1"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Role Category Breakdown
	currentCGI = 'roleid_breakdown.cgi'
	driver.find_element_by_partial_link_text("Role Category Breakdown").click(), time.sleep(5)
	expectedList = ["703","Transposon functions","Chemotaxis and motility",
			"Role category not yet assigned","Chlorophyll",
			"Hypothetical proteins","94"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to overlap summary
	currentCGI = 'overlap_summary.cgi'
	driver.find_element_by_partial_link_text("Overlap Summary").click(), time.sleep(5)
	expectedList = ["VAC_148","170895","171202","44 nucleotides","VAC_150","171040","171202",
			"VAC_5210","5173634","5174493","35 nucleotides","VAC_5211","5174340","5174493"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')

######### Go to GCP from overlap summary
	driver.find_element_by_partial_link_text("VAC_148").click(), time.sleep(10)
	expectedList = ["VAC_148","171084","170896","62","None assigned","BER SKIM"]
	overlap_window = driver.window_handles[0]
	gcp_window = driver.window_handles[1]
	driver.switch_to_window(gcp_window)
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'go to GCP')
	driver.close()
	driver.switch_to_window(overlap_window)
	driver.find_element_by_partial_link_text("Home").click() 

######### Test going to GCP
	currentCGI = 'ORF_infopage.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_241')
	gatewayForm.submit(), time.sleep(5)
	expectedList = ["VAC_241","end5/end3:","550","undecaprenyl phosphate","GO:0016763","Cellular processes",
			"Start confidence not calculated","Frameshift Name","EVIDENCE PICTURE","PF02366.13",
			"COG1807","No prosite data available","0.209","0.365","CHARACTERIZED MATCH","UniRef100_B1X8X0"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click() 

######### Test changing db
	currentCGI = 'gateway.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('abau')
	gatewayForm.submit(), time.sleep(2)
	expectedList = ["Acinetobacter baumannii ATCC 17978"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'change db')

######### Revert to test db
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC_test')
	gatewayForm.submit(), time.sleep(2)
	expectedList = ["Escherichia coli VAC1"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'change db back')

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
	gatewayForm.submit(), time.sleep(10) # let BLASTN run
	expectedList = ["(720 letters)","VAC_241","1427","VAC_2870","VAC_1732",
			"4,590,078","(28.2 bits)","Effective search space: 3172774528"]
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
	gatewayForm.submit(), time.sleep(10) # let BLAST run
	expectedList = ["(128 letters)","VAC_244","192","6e-51","VAC_3061",
			"1,139,576","(22.7 bits)","Effective search space: 61537104"]
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
	gatewayForm.submit(), time.sleep(10) # let TBLASTN run
	expectedList = ["(451 letters)","VAC.pseudomolecule.1","866","0.0",
			"1,748,284","(26.2 bits)","Effective search space: 629382240"]
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
	gatewayForm.submit(), time.sleep(2)

	##########################################
	########## TESTING FN = DUMPERS ##########
	##########################################

	# Overestimate dumper time to ensure it completes
	# Find the most recent DL of this particular file and compare to reference

	pathToDataDumps = '/Users/jmatsumura/Downloads/VAC1_test2'
		
######### GO Annotation
	currentCGI = 'nucleotide_dumper.cgi'
	driver.find_element_by_partial_link_text('GO Annotation').click(), time.sleep(180)
	result = compare_dl_files('GO_annotation.txt')
	log_results(currentCGI, result, fileName, 'GO dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Annotation
	# need to handle this a little differently to avoid clicking GO Annotation
	driver.find_element_by_id('just_annotation').click(), time.sleep(120)
	result = compare_dl_files('annotation.txt')
	log_results(currentCGI, result, fileName, 'Annotation dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Coords
	driver.find_element_by_partial_link_text('Gene Coordinates').click(), time.sleep(40)
	result = compare_dl_files('coord.txt')
	log_results(currentCGI, result, fileName, 'Coords dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Nucleotides
	driver.find_element_by_partial_link_text('Gene Nucleotide Sequence').click(), time.sleep(40) 
	result = compare_dl_files('nucleotide_multifasta_seq.fsa')
	log_results(currentCGI, result, fileName, 'Nucleotide dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Protein seqs
	driver.find_element_by_partial_link_text('Protein Sequence').click(), time.sleep(40)
	result = compare_dl_files('protein_multifasta_seq.fsa')
	log_results(currentCGI, result, fileName, 'Protein dumper')
	driver.find_element_by_partial_link_text("Home").click() 

######### Whole Genome
	driver.find_element_by_partial_link_text('Whole Genome Nucleotide Sequence').click(), time.sleep(40)
	result = compare_dl_files('whole_genome.txt')
	log_results(currentCGI, result, fileName, 'Whole genome')
	driver.find_element_by_partial_link_text("Home").click() 

######### GenBank
	driver.find_element_by_partial_link_text('GenBank Format').click(), time.sleep(120)
	result = compare_dl_files('gbk')
	log_results(currentCGI, result, fileName, 'GenBank')
	driver.find_element_by_partial_link_text("Home").click() 

######### GFF3
	driver.find_element_by_partial_link_text('GFF3 Format').click(), time.sleep(120)
	result = compare_dl_files('gff3')
	log_results(currentCGI, result, fileName, 'GFF3')
	driver.find_element_by_partial_link_text("Home").click() 

######### TBL
	driver.find_element_by_partial_link_text('TBL Format').click(), time.sleep(120)
	result = compare_dl_files('tbl')
	log_results(currentCGI, result, fileName, 'TBL')
	driver.find_element_by_partial_link_text("Home").click() 

##########################################
#### TESTING SUITE = ORF_infopage.cgi ####
##########################################
# This section will test all the potential links that a user could
# used on the GCP. Already know it loads fine, so navigate to the 
# same page. 

	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('new_db')
	dbBox.send_keys('VAC_test')
	gatewayForm.submit(), time.sleep(2)

	currentCGI = 'ORF_infopage.cgi'
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_241')
	gatewayForm.submit(), time.sleep(5)

	# For those pages which open new windows, handle using window_handles
	gateway_window = driver.window_handles[0]

	##########################################
	### TESTING PAGE = GC_Skew_Display.cgi ###
	##########################################
	currentCGI = 'GC_Skew_Display.cgi'
	driver.find_element_by_css_selector('#gcskew').click(), time.sleep(10)
	gcskew_window = driver.window_handles[1]
	driver.switch_to_window(gcskew_window)
	expectedList = ["Extended off end5: 600","Frame"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')

	ext5 = driver.find_element_by_name('extend5')
	ext3 = driver.find_element_by_name('extend3')
	for x in range(0,3):
		ext5.send_keys(Keys.BACKSPACE) 
	ext5.send_keys("700")
	for x in range(0,3):
		ext3.send_keys(Keys.BACKSPACE) 
	ext3.send_keys("850")
	driver.find_element_by_css_selector('.redraw').click(), time.sleep(3)
	expectedList = ["Extended off end5: 700","Extended off end3: 850"] 
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'redraw')
	driver.close()

	driver.switch_to_window(gateway_window)

######### Make sure sequence data can be displayed
	driver.find_element_by_css_selector('#viewsequence').click(), time.sleep(8)
	seqdisplay_window = driver.window_handles[1]
	driver.switch_to_window(seqdisplay_window)
	expectedList = ["1653 nucleotides","550 amino acids", 
			"ATGAAATCGGTACGTTACCTTATCGGCCTCTTCGCATTTATTGCCTGCTATTACCTGTTA",
			"CGTCTGGTGCTAATTCAGTATCGGCCCAAATGA",
			"MKSVRYLIGLFAFIACYYLLPISTRLLWQPDETRYAEISREMLASGDWIVPHLLGLRYFE",
			"RLVLIQYRPK"]
	result = verify_results(expectedList)	
	log_results('seq_display.cgi', result, fileName, 'load')
	driver.close()
	driver.switch_to_window(gateway_window)

	##########################################
	#### TESTING PAGE = btab_display.cgi #####
	##########################################

######## Test the links within the btab display
	currentCGI = 'btab_display.cgi'
	driver.find_element_by_partial_link_text('View BER Searches').click(), time.sleep(5)
	ber_window = driver.window_handles[1]
	driver.switch_to_window(ber_window)
	expectedList = ["UniRef100_B1X8X0","UniRef100_D7ZXT5","VAC.CDS.9803630974.1", 
			"VAC.CDS.9803630974.1","%Identity = 98.7","%Similarity = 99.5"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'BER Searches Display')

######## TESTING LINK = UniRef #######
	driver.find_element_by_partial_link_text('UniRef100_B1X8X0').click(), time.sleep(10)
	uniref_window = driver.window_handles[2]
	driver.switch_to_window(uniref_window)
	expectedList = ["Undecaprenyl phosphate-alpha","ARNT_ECODH",
			"UniProt","UniRef100_B1X8X0"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'UniProt/UniRef')
	driver.close() 
	driver.switch_to_window(ber_window)
	driver.close() 
	driver.switch_to_window(gateway_window)

	######################
	## LINKS WITHIN GCP ##
	######################

	currentCGI = 'ORF_infopage.cgi'
######## TESTING LINK = ExPASy #######
	driver.find_element_by_partial_link_text('EC number(s)').click(), time.sleep(20)
	expasy_window = driver.window_handles[1]
	driver.switch_to_window(expasy_window)
	expectedList = ["Lipid IV(A) 4-amino-4-deoxy-L-arabinosyltransferase",
			"2.4.2.43"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'ExPASy ENZYME')
	driver.close()
	driver.switch_to_window(gateway_window)
	
######## TESTING LINK = Gene Ontology #######
	driver.find_element_by_partial_link_text('GO:0009103').click(), time.sleep(20)
	amigo_window = driver.window_handles[1]
	driver.switch_to_window(amigo_window)
	expectedList = ["lipopolysaccharide biosynthetic process",
			"GO:0009103","gosubset_prok"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'AmiGO 2')
	driver.close()
	driver.switch_to_window(gateway_window)

######## TESTING LINK = AmiGO Search #######
	driver.find_element_by_partial_link_text('Search AmiGO').click(), time.sleep(20)
	amigo2_window = driver.window_handles[1]
	driver.switch_to_window(amigo2_window)
	expectedList = ["AmiGO 2"] # Cautious about what will change on the site
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'AmiGO Search')
	driver.close()
	driver.switch_to_window(gateway_window)

######## TESTING LINK = Gene Ontology Evidence #######
	driver.find_element_by_partial_link_text('IEA').click(), time.sleep(20)
	geneOntology_window = driver.window_handles[1]
	driver.switch_to_window(geneOntology_window)
	expectedList = ["Inferred from Electronic Annotation (IEA)",
			"Experimental Evidence Codes","NAS"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'Gene Ontology')
	driver.close()
	driver.switch_to_window(gateway_window)

######## TESTING LINK = Pfam #######
	driver.find_element_by_partial_link_text('PF13231.1').click(), time.sleep(20)
	pfam_window = driver.window_handles[1]
	driver.switch_to_window(pfam_window)
	expectedList = ["Dolichyl-phosphate-mannose-protein mannosyltransferase",
			"PF02366"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'Pfam')
	driver.close()
	driver.switch_to_window(gateway_window)

######## TESTING LINK = COG #######
	driver.find_element_by_partial_link_text('COG1807').click(), time.sleep(20)
	cog_window = driver.window_handles[1]
	driver.switch_to_window(cog_window)
	expectedList = ["4-amino-4-deoxy-L-arabinose transferase or related glycosyltransferase",
			"ArnT","COG1807"]
	result = verify_results(expectedList)	
	log_results("link", result, fileName, 'Pfam')
	driver.close()
	driver.switch_to_window(gateway_window)

	##########################################
	#### TESTING PAGE = sigp_display.cgi #####
	##########################################

	currentCGI = 'sigp_display.cgi'
	driver.find_element_by_partial_link_text('Graphical Display').click(), time.sleep(8)
	sigp_window = driver.window_handles[1]
	driver.switch_to_window(sigp_window)
	expectedList = ["VAC.transcript.9803630972.1",
			"Please configure the options below","Download raw SignalP"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'SigP graphical output')

######## Make sure SigP output can be downloaded
	driver.find_element_by_partial_link_text('here').click(), time.sleep(10)
	result = compare_dl_files('sigp')
	log_results(currentCGI, result, fileName, 'SigP Download')

######## Make sure SigP can be run on the fly
	aaBox = driver.find_element_by_name('aa_length')
	aaBox.send_keys(Keys.BACKSPACE)
	aaBox.send_keys(Keys.BACKSPACE)
	aaBox.send_keys("80")
	time.sleep(3)
	oType = driver.find_element_by_name('type')
	for option in oType.find_elements_by_tag_name('option'):
    	    if option.text == ' gram+ ':
        	option.click() 
        	break

	sigpForm = driver.find_element_by_name('submit')
	sigpForm.submit(), time.sleep(10)
	expectedList = ["VAC.transcript.9803630972.1",
			"Please configure the options below","Download raw SignalP"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'SigP rerun')
	driver.close()
	driver.switch_to_window(gateway_window)
	driver.find_element_by_partial_link_text("Home").click() 

######## Make sure role IDs can be added and deleted.
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_5315')
	gatewayForm.submit()

	currentCGI = 'ORF_infopage.cgi'
	addRole = driver.find_element_by_name('add_role')
	delRole = driver.find_element_by_name('del_role')
	addRole.send_keys("102")
	delRole.send_keys("703")
	driver.find_element_by_partial_link_text("submit").click(), time.sleep(5)
	expectedList = ["The role_link table has been updated","VAC_5315",
			"1280","102","Central intermediary metabolism","Other"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'add role')
	result = notFoundInPage("703")	
	log_results(currentCGI, result, fileName, 'delete role')

	# Need to revert to earlier state for the next round of checks
	addRole = driver.find_element_by_name('add_role')
	delRole = driver.find_element_by_name('del_role')
	addRole.send_keys("703")
	delRole.send_keys("102")
	driver.find_element_by_partial_link_text("submit").click(), time.sleep(5)

######## Make sure Gene Identification panel can be updated.
	geneBox = driver.find_element_by_name('edit_gene_sym')
	geneBox.send_keys('tesT123')
	driver.find_element_by_partial_link_text("submit").click(), time.sleep(5)
	expectedList = ["Annotation has been updated","tesT123"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'Gene Identification Panel')

	# revert
	geneBox = driver.find_element_by_name('edit_gene_sym')
	for x in range(0,8):
		geneBox.send_keys(Keys.BACKSPACE) 
	driver.find_element_by_partial_link_text("submit").click(), time.sleep(5)

	driver.find_element_by_partial_link_text("Home").click() 

##########################################
##### TESTING SUITE = ann_tools.cgi ######
##########################################

	driver.find_element_by_partial_link_text("Search/Browse").click() 

######## Check all categories, ordered by role category
	currentCGI = 'submit_begin_all.cgi'
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(12)
	expectedList = ["All categories","Viral functions","other roles","VAC_767",
			"1293565","3-deoxy-7-phosphoheptulonate synthase","VAC_1557"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'all category load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 

######## Check sorting by just DNA metabolism role category
	oType = driver.find_element_by_name('role_order')
	for option in oType.find_elements_by_tag_name('option'):
    	    if option.text == 'DNA metabolism':
        	option.click() 
        	break
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(12)
	expectedList = ["All categories","Viral functions","other roles","VAC_523","850048",
			"5'-3' exonuclease, C-terminal SAM fold family protein","VAC_2367"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'single category load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 

######## Check sorting by just role ID 93
	roleIdBox = driver.find_element_by_name('role_id')
	for x in range(0,7): # there must be a better way!
		roleIdBox.send_keys(Keys.BACKSPACE) 
	roleIdBox.send_keys("93"), time.sleep(3)
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(12)
	expectedList = ["All categories","Viral functions","other roles","VAC_384","416094",
			"septum site-determining protein MinD","VAC_2621"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'single role id load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 

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
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 

######### Go to Role Category Breakdown (need to make sure link works from this page) 
	currentCGI = 'roleid_breakdown.cgi'
	driver.find_element_by_partial_link_text("ROLE CATEGORY BREAKDOWN").click(), time.sleep(10)
	expectedList = ["703","Transposon functions","Chemotaxis and motility",
			"Role category not yet assigned","Chlorophyll",
			"Hypothetical proteins","94"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.execute_script("window.history.go(-1)")  

	'''
	## THIS IS A PLACE HOLDER LIST UNTIL THE FILES ARE LOADED FOR PRODUCTION ##
######### Go to Interevidence Search 
	currentCGI = 'interevidence_search.cgi'
	driver.find_element_by_partial_link_text("INTEREVIDENCE SEARCH RESULTS").click(), time.sleep(20)
	expectedList = ["Escherichia coli 4_1","100.0",
			"Fimbrial protein","94.4"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 
	'''

######### Search single query term 
	currentCGI = 'search_ident.cgi'
	oType = driver.find_element_by_id('selectOption')
	for option in oType.find_elements_by_tag_name('option'):
    	    if option.text == 'EC number':
        	option.click() 
        	break
	queryBox = driver.find_element_by_name('queryWord')
	queryBox.send_keys('2.1')
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(10)
	expectedList = ["VAC_106","VAC_2850","2932255","uraH",
			"2.1.1.-","argininosuccinate lyase","transaldolase"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("SEARCH AGAIN").click() 

######### Search using combinatorial queries 
	currentCGI = 'search_ident.cgi'
	queryBox = driver.find_element_by_name('queryWord')
	queryBox.send_keys('kinase')
	driver.find_element_by_css_selector('.searchMore').click()
	driver.find_element_by_css_selector('.searchMore').click()
	oType = driver.find_element_by_id('sel1')
	for option in oType.find_elements_by_tag_name('option'):
    	    if option.text == 'EC number':
        	option.click() 
        	break
	oType = driver.find_element_by_id('sel2')
	for option in oType.find_elements_by_tag_name('option'):
    	    if option.text == 'GO ID':
        	option.click() 
        	break
	queryBox = driver.find_element_by_name('inp1')
	queryBox.send_keys('2.7')
	queryBox = driver.find_element_by_name('inp2')
	queryBox.send_keys('GO:0004417')
	sbForm = driver.find_element_by_name('form1')
	sbForm.submit(), time.sleep(10)
	expectedList = ["VAC_78","91858","kinase","contains",
			"120","103","1"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'load')
	driver.find_element_by_partial_link_text("Home").click(), time.sleep(5)

##########################################
### TESTING SUITE = genome_viewer.cgi ####
##########################################
# Since this page is primarily built as a graphical interface, the way
# these tests will be performed will be a bit different. ActionChains
# will be created which simulate, step by step, the mouse and click movements
# that a user would use in order to do actions like insertions, deletions,
# changing starts/stops, and merging genes. 
#
# The pixel positions here are extremely finicky, must use VAC_test (or VAC1_test2) 
# to maintain consistency of positions for the gene graphics. 
	currentCGI = 'genome_viewer.cgi'
	gv_link = driver.find_element_by_partial_link_text("Genome Viewer")
	ActionChains(driver).key_down(Keys.COMMAND).move_to_element(gv_link).click().key_up(Keys.COMMAND).perform(), time.sleep(20)
	gateway_window = driver.window_handles[0] # need to perform verifications of GV changes through GCP
	gv_window = driver.window_handles[1]
	driver.switch_to_window(gv_window)

######### Check gene insertion 
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,85
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("Edit").click(), time.sleep(10)
	x,y = 29,173
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("Insert").click(), time.sleep(2)
	driver.find_element_by_css_selector('#insert_orf_submit').click(), time.sleep(2)
	alert = driver.switch_to_alert()
	alert.accept(), time.sleep(20)
	result = gvCheck('#gene_image')	
	log_results(currentCGI, result, fileName, 'insert gene')

######### Check merge genes, first have to insert another gene
	driver.find_element_by_css_selector('#VAC_5').click(), time.sleep(5) # reposition
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,85
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("Edit").click(), time.sleep(10)
	x,y = -2,173
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("Insert").click(), time.sleep(2)
	driver.find_element_by_css_selector('#insert_orf_submit').click(), time.sleep(2)
	alert = driver.switch_to_alert()
	alert.accept(), time.sleep(20)
	result = gvCheck('#gene_image')	
	log_results(currentCGI, result, fileName, 'insert gene round 2')

	# Two genes have been inserted, now merge
	driver.find_element_by_css_selector('#VAC_5').click(), time.sleep(5) # reposition
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 26,-32
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("merge").click(), time.sleep(2)
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = -4,-32
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("merge").click(), time.sleep(2)
	driver.find_element_by_css_selector("#mergeButton").click(), time.sleep(25)
	result = gvCheck('#gene_image')	
	log_results(currentCGI, result, fileName, 'merge genes')

######### Check gene deletion 
	driver.find_element_by_css_selector('#VAC_5').click(), time.sleep(5) # reposition
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 26,-5
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(2)
	driver.find_element_by_partial_link_text("Delete").click(), time.sleep(2)
	alert = driver.switch_to_alert()
	alert.accept(), time.sleep(20)
	result = gvCheck('#gene_image')	
	log_results(currentCGI, result, fileName, 'delete gene')
	
######### Check update stop site
	driver.find_element_by_css_selector('#VAC_5').click(), time.sleep(5) # reposition
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,85
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(3)
	driver.find_element_by_partial_link_text("Edit").click(), time.sleep(20)
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,660
	seq_display = driver.find_element_by_css_selector('#seq_display')
	ActionChains(driver).move_to_element(seq_display).click().perform(), time.sleep(2)
	for i in range(0,191): # scroll to correct position
		ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
		time.sleep(.1)
	x,y = 23,18 # stop AA 
	time.sleep(1) 
	ActionChains(driver).move_to_element(seq_display).move_by_offset(x,y).click().perform(), time.sleep(3)
	driver.find_element_by_partial_link_text("Move Stop Site Here").click(), time.sleep(8)
	stop_confirm_window = driver.window_handles[2]
	driver.switch_to_window(stop_confirm_window)
	driver.find_element_by_css_selector('.startStopConfirm').click(), time.sleep(20)
	
	# Stop site has been "moved" (although to same position) and now needs to be verified in GCP
	driver.switch_to_window(gateway_window)
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_6')
	gatewayForm.submit(), time.sleep(5)
	expectedList = ["VAC_6","end5/end3:","6117","4909","402","1209"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'move stop -- coords check')
	driver.find_element_by_css_selector('#viewsequence').click(), time.sleep(8)
	seqdisplay_window = driver.window_handles[2]
	driver.switch_to_window(seqdisplay_window)
	expectedList = ["1209 nucleotides","402 amino acids", 
			"ATGAAACTTGCATTAATCATTGATGATTATTTGCCCCATAGCACACGCGTTGGGGCTAAA",
			"TGCGTTTAG",
			"MKLALIIDDYLPHSTRVGAKMFHELGLELLSRGHDVTVITPDISLQAIYSISMIDGIKVW",
			"LLSDSVLRKQLGQNANVLLKSQFSVESAAHTIEVRLEAGECV"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'move stop -- seq check')
	driver.close()
	driver.switch_to_window(gv_window)

######### Check update start site
	# While this is very similar to the last block, instead of making a function 
	# out of these two, keep them separate for more customizable checks later.
	driver.find_element_by_css_selector('#VAC_5').click(), time.sleep(5) # reposition
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,85
	ActionChains(driver).move_to_element(gene_img).move_by_offset(x,y).click().perform(), time.sleep(3)
	driver.find_element_by_partial_link_text("Edit").click(), time.sleep(20)
	gene_img = driver.find_element_by_css_selector('#gene_image')
	x,y = 70,660
	seq_display = driver.find_element_by_css_selector('#seq_display')
	ActionChains(driver).move_to_element(seq_display).click().perform(), time.sleep(2)
	for i in range(0,455): # scroll to correct position
		ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
		time.sleep(.1)
	x,y = 290,18 # start AA 
	time.sleep(1) 
	ActionChains(driver).move_to_element(seq_display).move_by_offset(x,y).click().perform(), time.sleep(3)
	driver.find_element_by_partial_link_text("Move Start Site Here").click(), time.sleep(8)
	stop_confirm_window = driver.window_handles[2]
	driver.switch_to_window(stop_confirm_window)
	driver.find_element_by_css_selector('.startStopConfirm').click(), time.sleep(20)

	# Start site has been "moved" (although to same position) and now needs to be verified in GCP
	driver.switch_to_window(gateway_window)
	gatewayForm = driver.find_element_by_name('form1')
	dbBox = driver.find_element_by_name('orf')
	dbBox.send_keys('VAC_6')
	gatewayForm.submit(), time.sleep(5)
	expectedList = ["VAC_6","end5/end3:","6117","4909","402","1209"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'move start -- coords check')
	driver.find_element_by_css_selector('#viewsequence').click(), time.sleep(8)
	seqdisplay_window = driver.window_handles[2]
	driver.switch_to_window(seqdisplay_window)
	expectedList = ["1209 nucleotides","402 amino acids", 
			"ATGAAACTTGCATTAATCATTGATGATTATTTGCCCCATAGCACACGCGTTGGGGCTAAA",
			"TGCGTTTAG",
			"MKLALIIDDYLPHSTRVGAKMFHELGLELLSRGHDVTVITPDISLQAIYSISMIDGIKVW",
			"LLSDSVLRKQLGQNANVLLKSQFSVESAAHTIEVRLEAGECV"]
	result = verify_results(expectedList)	
	log_results(currentCGI, result, fileName, 'move start -- seq check')
	driver.close()
	driver.switch_to_window(gv_window)

	time.sleep(5)

	driver.close()
	driver.switch_to_window(gateway_window)

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

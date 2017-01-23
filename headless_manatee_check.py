#!/usr/bin/python

# This is a modified version of the crawler/health_check scripts that runs
# headless via PhantomJS. This is to get around issues with dependency 
# updates with both Chrome and the Chrome driver. 

import sys, time
from selenium import webdriver

def main():

    username =  str(sys.argv[1]) # let the user specify username
    password =  str(sys.argv[2]) # let the user specify password
    db	=  str(sys.argv[3]) # let the user specify db

    driver = webdriver.PhantomJS(r'/usr/bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    driver.set_window_size(1100,900)
    driver.set_window_position(0,0)
    driver.get("https://manatee.igs.umaryland.edu")

######## Check that login and home page is correct
    expectedList = ["user_name","password","database"]
    result = verify_results(expectedList)	

######## Now login and make sure gateway is fine
    userBox = driver.find_element_by_name('user')
    pwBox = driver.find_element_by_name('password')
    dbBox = driver.find_element_by_name('db')
    loginForm = driver.find_element_by_name('login_form')
    userBox.send_keys(username)
    pwBox.send_keys(password)
    dbBox.send_keys(db)
    loginForm.submit(), time.sleep(5)

##########################################
##### TESTING SUITE = gateway.cgi ######
##########################################

    expectedList = ["Access Annotation","Sequence Search",
                "Change Organism Database", "Data file downloads"]
    result = verify_results(expectedList)

######### Go to Genome Viewer
	currentCGI = 'genome_viewer.cgi'
	driver.find_element_by_partial_link_text("Genome Viewer").click(), time.sleep(15)
	expectedList = ["Find Orf","Coord Search"]
	result = verify_results(expectedList)	
	driver.back() # currently, genome viewer has no home link

######### Go to Genome Statistics
	currentCGI = 'summary_page.cgi'
	driver.find_element_by_partial_link_text("Genome Statistics").click(), time.sleep(5)
	expectedList = ["24.8%","25.7%","24.9%","24.6%","Genome Summary",
			"1100","tRNA","5245125 bp"]
	result = verify_results(expectedList)	

######### Go to RNA display page
	currentCGI = 'display_feature.cgi'
	driver.find_element_by_partial_link_text('tRNA').click(), time.sleep(5)
	expectedList = ["VAC_171","VAC_5307","tRNA-Pro","VAC.pseudomolecule.1"]
	result = verify_results(expectedList)	
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to Role Category Breakdown
	currentCGI = 'roleid_breakdown.cgi'
	driver.find_element_by_partial_link_text("Role Category Breakdown").click(), time.sleep(5)
	expectedList = ["703","Transposon functions","Chemotaxis and motility",
			"Role category not yet assigned","Chlorophyll",
			"Hypothetical proteins","94"]
	result = verify_results(expectedList)	
	driver.find_element_by_partial_link_text("Home").click() 

######### Go to overlap summary
	currentCGI = 'overlap_summary.cgi'
	driver.find_element_by_partial_link_text("Overlap Summary").click(), time.sleep(5)
	expectedList = ["VAC_148","170895","171202","44 nucleotides","VAC_150","171040","171202",
			"VAC_5210","5173634","5174493","35 nucleotides","VAC_5211","5174340","5174493"]
	result = verify_results(expectedList)	

######### Go to GCP from overlap summary
	driver.find_element_by_partial_link_text("VAC_148").click(), time.sleep(10)
	expectedList = ["VAC_148","171084","170896","62","None assigned","BER SKIM"]
	overlap_window = driver.window_handles[0]
	gcp_window = driver.window_handles[1]
	driver.switch_to_window(gcp_window)
	result = verify_results(expectedList)	
	driver.close()
	driver.switch_to_window(overlap_window)
	driver.find_element_by_partial_link_text("Home").click() 

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


##########################################
######## TESTING SUITE = dumpers #########
##########################################

######### Coords
	#driver.find_element_by_partial_link_text('Gene Coordinates').click(), time.sleep(60)
	#result = compare_dl_files('coord.txt')
	#driver.find_element_by_partial_link_text("Home").click() 
    #driver.quit()

    driver.quit() 

###################################
#########   FUNCTIONS   ###########
###################################

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
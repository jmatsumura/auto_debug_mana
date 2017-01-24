#!/usr/bin/python

# This is a modified version of the crawler/health_check scripts that runs
# headless via PhantomJS. This is to get around issues with dependency 
# updates with both Chrome and the Chrome driver. 

import sys, time, os
from selenium import webdriver

# Driver will be global so it's not such a pain to keep passing this across fxns.
driver = webdriver.PhantomJS(r'/usr/bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')

def main():

    username =  str(sys.argv[1]) # let the user specify username
    password =  str(sys.argv[2]) # let the user specify password
    db	=  str(sys.argv[3]) # let the user specify db

    driver.set_window_size(1100,900)
    driver.set_window_position(0,0)
    driver.get("https://manatee.igs.umaryland.edu")	

    time.sleep(5)

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
                "Change Organism Database","Data File Downloads"]
    verify_results(expectedList,'gateway.cgi')

######### Go to Genome Viewer

    # Note that for essentially all the links off the gateway a new window is
    # opened. Thus, need to be mindful and swap between the tabs correctly.
    gateway_window = driver.window_handles[0]

    driver.find_element_by_partial_link_text("Genome Viewer").click(), time.sleep(15)
    gv_window = driver.window_handles[1]
    driver.switch_to_window(gv_window)
    expectedList = ["Find Orf","Coord Search"]
    verify_results(expectedList,'genome_viewer.cgi')	
    driver.close() # done with GV for now
    driver.switch_to_window(gateway_window)

######### Go to Genome Statistics
    driver.find_element_by_partial_link_text("Genome Statistics").click(), time.sleep(5)
    gs_window = driver.window_handles[1]
    driver.switch_to_window(gs_window)
    expectedList = ["24.8%","25.7%","24.9%","24.6%","Genome Summary",
            "1100","tRNA","5245125 bp"]
    verify_results(expectedList,'summary_page.cgi')	

######### Go to RNA display page
    driver.find_element_by_partial_link_text('tRNA').click(), time.sleep(5)
    expectedList = ["VAC_171","VAC_5307","tRNA-Pro","VAC.pseudomolecule.1"]
    verify_results(expectedList,'display_feature.cgi')	
    driver.close() # done with genome statistics and tRNA windows
    driver.switch_to_window(gateway_window)

######### Go to Role Category Breakdown
    driver.find_element_by_partial_link_text("Role Category Breakdown").click(), time.sleep(5)
    rcb_window = driver.window_handles[1]
    driver.switch_to_window(rcb_window)
    expectedList = ["703","Transposon functions","Chemotaxis and motility",
            "Role category not yet assigned","Chlorophyll",
            "Hypothetical proteins","94"]
    verify_results(expectedList,'roleid_breakdown.cgi')	
    driver.close() # done with role category breakdown
    driver.switch_to_window(gateway_window)

######### Go to overlap summary
    driver.find_element_by_partial_link_text("Overlap Summary").click(), time.sleep(5)
    os_window = driver.window_handles[1]
    driver.switch_to_window(os_window)
    expectedList = ["VAC_148","170895","171202","44 nucleotides","VAC_150","171040","171202",
        "VAC_5210","5173634","5174493","35 nucleotides","VAC_5211","5174340","5174493"]
    verify_results(expectedList,'overlap_summary.cgi')	

######### Go to GCP from overlap summary
    driver.find_element_by_partial_link_text("VAC_148").click(), time.sleep(10)
    gcp_window = driver.window_handles[2]
    driver.switch_to_window(gcp_window)
    expectedList = ["VAC_148","171084","170896","62","None assigned","BER SKIM"]
    verify_results(expectedList,'ORF_infopage.cgi')	
    driver.close() # done with GCP
    driver.switch_to_window(os_window)
    driver.close() # done with overlap summary
    driver.switch_to_window(gateway_window)

######### Run BLASTN
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
    time.sleep(5)
    gatewayForm.submit(), time.sleep(10) # let BLASTN run
    expectedList = ["(720 letters)","VAC_241","1427","VAC_2870","VAC_1732",
        "4,590,078","(28.2 bits)","Effective search space: 3172774528"]
    verify_results(expectedList,'perform_blast.cgi')	
    driver.find_element_by_partial_link_text("Home").click() 

##########################################
##### TESTING SUITE = ann_tools.cgi ######
##########################################

    driver.find_element_by_partial_link_text("Search/Browse").click(), time.sleep(5)
    at_window = driver.window_handles[1]
    driver.switch_to_window(at_window)

######## Check that coord search is correct
    end5 = driver.find_element_by_name('end5')
    end3 = driver.find_element_by_name('end3')
    end5.send_keys("1000")
    end3.send_keys("5000")
    sbForm = driver.find_element_by_name('form1')
    sbForm.submit(), time.sleep(20)
    expectedList = ["VAC.pseudomolecule.1","VAC_4","VAC_5","VAC_6","gene name",
            "UDP-glucose 6-dehydrogenase","VAC_3","2746","1.1.1.44"]
    verify_results(expectedList,'coordinate_view.cgi')	
    driver.find_element_by_partial_link_text("SEARCH AGAIN").click(), time.sleep(5)
    driver.close()
    driver.switch_to_window(gateway_window)

##########################################
######## TESTING SUITE = dumpers #########
##########################################

# In order to guaranatee consistency, must switch to VAC1_test2 since this DB
# is not to be touched and should always output the same data from the dumpers.
	#gatewayForm = driver.find_element_by_name('form1')
	#dbBox = driver.find_element_by_name('new_db')
	#dbBox.send_keys('VAC1_test2')
	#gatewayForm.submit(), time.sleep(5)

######### Coords
	#driver.find_element_by_partial_link_text('Gene Coordinates').click(), time.sleep(60)
	#result = compare_dl_files('coord.txt')
	#driver.find_element_by_partial_link_text("Home").click() 
    #driver.quit()

### HACK ###
    # For now, since phantomjs can't handle file downloads, jut ping the 
    # ActiveMQ server to make sure it is up.
    response = os.system("ping -c 1 messaging.igs.umaryland.edu")
    if response != 0:
        print('Cannot reach messaging.igs.umaryland.edu')
        exit(1)

    driver.close()
    driver.quit() 
    exit(0)

###################################
#########   FUNCTIONS   ###########
###################################

# Function to try find expected text within a page. Accepts the text 
# that is to be parsed. Must be careful using this function as it 
# searches for text on the CURRENT page. Thus, be meticulous about 
# which page is currently being viewed currently.  
def find_in_page(text):

    result = 'SUCCESS'
    try:
        # Headless requires a bit of a different check.
        assert text.encode('utf-8') in driver.page_source.encode('utf-8')
    except:
        result = 'FAILURE' # if not in page, fail

    return result

# This function is used to check for all expected text on a 
# particular page. The input argument is a list of strings for
# what needs to be present on a particular page. 
def verify_results(listOfExpected,page): 

    for x in listOfExpected:

        result = find_in_page(x)

        if result == 'SUCCESS':
            pass 
        else: # must be FAILURE
            print('Cant find text {0} in page {1}'.format(x,page))
            exit(1)

        return None


if __name__ == '__main__':
	main()
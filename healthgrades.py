import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import re
import traceback
import time
from time import sleep
import signal
from selenium.webdriver.firefox.options import Options


options = webdriver.ChromeOptions()
options.add_argument("--headless")
browser=webdriver.Chrome(chrome_options=options,executable_path='/home/ubuntu/health_grade/chromedriver')

#This function scraps the code of all the states in the directory of the website- www.healthgrades.com
def get_states():
    
    page = "https://www.healthgrades.com/hospital-directory"
    print "Inside get_States"
    try:
        browser.get(page)
    except TimeoutException:
        print traceback.format_exc()
        browser.execute_script("window.stop();")
        with open("left.txt", "a") as f:
            f.write("\n")
            f.write(page)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    uniqueStatCode = []
    li = soup.find_all("li", class_="city__name")
    tempCityNames = []
    cityNames = []
    for i in li:
        cityName = i.find('a').text.encode('utf-8')
        tempCityNames.append(cityName)
   
    for c in tempCityNames:
        a = c.split(",")      
        cityNames.append(a[1].strip())
        
    for i in cityNames:
        if i not in uniqueStatCode:
            uniqueStatCode.append(i)

    print "uniqueStatCode=", uniqueStatCode
    return uniqueStatCode


#This function is called for each doctor to fetch the details like - Name, address, education, age, gender, ratings and comments, etc.
def get_doctor_details(uniqueDocLink, num):
     doctors = []
     print "uniqueDocLink", uniqueDocLink
     try:
           browser.implicitly_wait(10) 
           browser.get("https://www.healthgrades.com/" + uniqueDocLink)
                            
     except TimeoutException:
          print traceback.format_exc()
          browser.execute_script("window.stop();")
          with open("left.txt", "a") as f:
                                f.write("\n")
                                f.write(uniqueDocLink)                  
                        
     html = browser.page_source
     soup = BeautifulSoup(html, 'html.parser')
     try:
        name = soup.find("div", class_="provider-name").text.encode('utf-8')
     except AttributeError:
        name = "Unavailable"
     print "name", name
     title = "Unavailable"
     first_name = "Unavailable"
     last_name = "Unavailable"
     designation = "Unavailable"

     split_names = name.split(" ")
     try:
         title = split_names[0]
     except:
         title = "Unavailable"

     try:
         first_name = split_names[1]
     except:
         first_name = "Unavailable"

     try:
         last_name = split_names[2]
     except:
         last_name = "Unavailable"

     split_names = name.split(",")
     try:
         designation = split_names[1]
     except:
         designation = "Unavailable"   

     #SPECIALITY
     
     try:
         speciality = soup.find('div', class_='provider-speciality').text.encode("utf-8")
     except AttributeError:
         speciality = "Unavailable"

     #GENDER
     try:
         gender = soup.find('div', class_='provider-gender').text.encode("utf-8")
     except AttributeError:
         gender = "Unavailable"

     #AGE
     try:
         a = soup.find('div', class_='provider-age').text.encode("utf-8")
         temp = a.split(" ")
         age = temp[1]
     except AttributeError:
         age = "Unavailable"
     
     section_address = soup.find('section', class_="profile-standard-address-compare")
     try:
        workplace = section_address.find('h3', class_="hg-track js-profile-scroll-link").text.encode('utf-8')
     except AttributeError:
        workplace = "Unavailable"
        
     try:
        streetAddress = section_address.find('p', attrs={"itemprop": "streetAddress"}).text.encode('utf-8')
     except AttributeError:
        streetAddress = "Unavailable"

       
     try:
         remain_address = section_address.find('p', class_="city-state-info")
         try:
            addressLocality = remain_address.find('span', attrs={"itemprop": "addressLocality"}).text.encode('utf-8')
         except AttributeError:
            addressLocality = "Unavailable"

         try:
            addressRegion = remain_address.find('span', attrs={"itemprop": "addressRegion"}).text.encode('utf-8')
         except AttributeError:
            addressRegion = "Unavailable"
                               
         try:
            postalCode = remain_address.find('span', attrs={"itemprop": "postalCode"}).text.encode('utf-8')
         except AttributeError:
            postalCode = "Unavailable"
            
     except AttributeError:
        addressLocality = "Unavailable"
        addressRegion = "Unavailable"
        postalCode = "Unavailable"
        
  
     
                           

     try:
        phone = soup.find("h3",  class_="ps-contact-phone").text.encode('utf-8')
     except AttributeError:
        phone = "Unavailable"
     temp_ratings = soup.find('div', class_="score-details")
     rating_total_reviews = "Unavailable"
     rating_total_comments = "Unavailable"
     rating_total_stars = "Unavailable"


     try:
 	rating_total_stars = soup.find('div', class_="summary-stars").find('span', class_="rating-value").text.encode('utf-8')
     except:
	rating_total_stars = "Unavailable"


     try:
         if temp_ratings is not None:
                            temp_ratings_span = temp_ratings.find_all('span',class_="number")
                            if len(temp_ratings_span) == 1:
                                temp_list = temp_ratings.text.encode('utf-8').split(" ")
                                temp = temp_list[len(temp_list)-1]
                                if temp == "reviews":
                                  rating_total_reviews = temp_ratings_span[0].text.encode('utf-8')
                                elif temp == "comments":
                                  rating_total_comments = temp_ratings_span[0].text.encode('utf-8')
                            else:
                                if temp_ratings_span[0] is not None:
                                    rating_total_reviews = temp_ratings_span[0].text.encode('utf-8')
                                else:
                                    rating_total_reviews = "Unavailable"
                                    
                                if temp_ratings_span[1] is not None:
                                    rating_total_comments = temp_ratings_span[1].text.encode('utf-8')
                                else:
                                    rating_total_comments = "Unavailable"
     except TypeError:
        rating_total_reviews = "Unavailable"
        rating_total_comments = "Unavailable"
                                  
     rating_group = soup.find('div',class_="average-rating-group")
     rating_group_title = []
     rating_group_title_score = []
     rating_group_title = soup.find_all('div',class_="title")
     rating_group_title_score = soup.find_all('span',class_="tooltip-numerator")
     
     try:
        trustworthiness = rating_group_title_score[0].text.encode('utf-8')
     except:
          trustworthiness = "Unavailable"
     
     try:
        explains_condition_well = rating_group_title_score[1].text.encode('utf-8')
     except:
          explains_condition_well = "Unavailable"
     
     try:
        answers_question = rating_group_title_score[2].text.encode('utf-8')
     except:
          answers_question = "Unavailable"

     try:
         time_well_spent = rating_group_title_score[3].text.encode('utf-8')
     except:
          time_well_spent = "Unavailable"
        
     try:
          schedulling = rating_group_title_score[4].text.encode('utf-8')
     except:
        schedulling = "Unavailable"
     
     try:
         office_environment = rating_group_title_score[5].text.encode('utf-8')
     except:
        office_environment = "Unavailable"
     
     try:
         staff_friendliness = rating_group_title_score[6].text.encode('utf-8')
     except:
        staff_friendliness = "Unavailable"  
     
     try:
         wait_time_bar = soup.find('div',class_="wait-time-bar")
         average_Wait_Time = wait_time_bar.text.encode('utf-8')
     except:
        average_Wait_Time = "Unavailable"

     #EDUCATION
     education_section = soup.find('section',attrs={"data-qa-target": "learn-education-section"})
     ul=None
     try:
        ul = education_section.find('ul')
     except:
	blah='do nothing'
     education_one = "Unavailable"
     education_type_one = "Unavailable"
     education_year_one = "Unavailable"
     education_two = "Unavailable"
     education_type_two = "Unavailable"
     education_year_two = "Unavailable"
     education_three = "Unavailable"
     education_type_three = "Unavailable"
     education_year_three = "Unavailable"

     if ul is not None:
             li = ul.find_all('li')
	     size = len(li)
		     if li[size-1] is not None:
		         temp = li[size-1].find_all('div')
		         education_one = temp[0].text.encode('utf-8')
		         if len(temp) > 1:
		             a = temp[1].text.encode('utf-8').split("|")
		             education_type_one = a[0]
		             if len(a) > 1:
		                 education_year_one = a[1]

	             if size > 1:
			     if li[size-2] is not None:
				 temp = li[size-2].find_all('div')
				 education_two = temp[0].text.encode('utf-8')
				 if len(temp) > 1:
				     a = temp[1].text.encode('utf-8').split("|")
				     education_type_two = a[0]
				     if len(a) > 1:
				         education_year_two = a[1]

		     if size > 2:
			     if li[size-3] is not None:
				 temp = li[size-3].find_all('div')
				 education_three = temp[0].text.encode('utf-8')
				 if len(temp) > 1:
				     a = temp[1].text.encode('utf-8').split("|")
				     education_type_three  = a[0]
				     if len(a) > 1:
				         education_year_three  = a[1]
       
     #ADMITING PRIVILIDGES
     admiting_privilidges_section = soup.find('section',attrs={"data-qa-target": "learn-certifications-section"})
     sections=list()
     try:
         sections = admiting_privilidges_section.find_all('section')
     except:
         blah='do nothing'
     admiting_privilidge_one = "Unavailable"
     admiting_privilidge_streetAddress_one = "Unavailable"
     admiting_privilidge_addressLocality_one = "Unavailable"
     admiting_privilidge_addressRegion_one = "Unavailable"
     admiting_privilidge_postalCode_one = "Unavailable"
     admiting_privilidge_two = "Unavailable"
     admiting_privilidge_streetAddress_two  = "Unavailable"
     admiting_privilidge_addressLocality_two  = "Unavailable"
     admiting_privilidge_addressRegion_two  = "Unavailable"
     admiting_privilidge_postalCode_two = "Unavailable"
     if len(sections) > 0:
         s = sections[0].find('address')
         admiting_privilidge_one = s.find('a').text.encode('utf-8')
         admiting_privilidge_streetAddress_one = s.find('div', attrs={'itemprop':'streetAddress'}).text.encode('utf-8')
         admiting_privilidge_addressLocality_one = s.find('span', attrs={'itemprop':'addressLocality'}).text.encode('utf-8')
         admiting_privilidge_addressRegion_one = s.find('span', attrs={'itemprop':'addressRegion'}).text.encode('utf-8')
         admiting_privilidge_postalCode_one = s.find('span', attrs={'itemprop':'postalCode'}).text.encode('utf-8')


         if len(sections) > 1:
             s = sections[1].find('address')
             admiting_privilidge_two = s.find('a').text.encode('utf-8')
             admiting_privilidge_streetAddress_two = s.find('div', attrs={'itemprop':'streetAddress'}).text.encode('utf-8')
             admiting_privilidge_addressLocality_two = s.find('span', attrs={'itemprop':'addressLocality'}).text.encode('utf-8')
             admiting_privilidge_addressRegion_two = s.find('span', attrs={'itemprop':'addressRegion'}).text.encode('utf-8')
             admiting_privilidge_postalCode_two = s.find('span', attrs={'itemprop':'postalCode'}).text.encode('utf-8')
     
     #Board Certificates
     board_certificates_section = soup.find('section',attrs={"data-qa-target": "learn-certifications-section"})
     ul=None
     try:
         ul = board_certificates_section.find('ul')
     except:
         blah='blahblahblah'
     board_certificates_one = "Unavailable"
     board_certificates_one_accredited_by = "Unavailable"
     board_certificates_two = "Unavailable"
     board_certificates_two_accredited_by = "Unavailable"
     board_certificates_three = "Unavailable"
     board_certificates_three_accredited_by = "Unavailable"
     if ul is not None:
         li = ul.find_all('li')
         try:
             temp = li[0].find_all('div')
             board_certificates_one = temp[0].text.encode('utf-8')
             a = temp[1].text.encode('utf-8').split(":")
             board_certificates_one_accredited_by = a[1]
         except AttributeError, IndexError:
             board_certificates_one = "Unavailable"
             board_certificates_one_accredited_by = "Unavailable"

         

         if len(li) > 1:

             try:
                 temp = li[1].find_all('div')
                 board_certificates_two = temp[0].text.encode('utf-8')
                 a = temp[1].text.encode('utf-8').split(":")
                 board_certificates_two_accredited_by = a[1]
             except AttributeError, IndexError:
                 board_certificates_two = "Unavailable"
                 board_certificates_two_accredited_by = "Unavailable"

             

             if len(li) > 2:

                 try:
                     temp = li[2].find_all('div')
                     board_certificates_three = temp[0].text.encode('utf-8')
                     a = temp[1].text.encode('utf-8').split(":")
                     board_certificates_three_accredited_by = a[1]
                 except AttributeError, IndexError:
                     board_certificates_three = "Unavailable"
                     board_certificates_three_accredited_by = "Unavailable"

   
     if soup.find('div', class_="show-more-container") is not None:
                            comment_page_url = soup.find('div', class_="show-more-container").find('a')['href']
                            comment_page_url = "https:" + comment_page_url
                            try:
                                   browser.implicitly_wait(10) 
                                   browser.get(comment_page_url)
                                                    
                            except TimeoutException:
                                  print traceback.format_exc()
                                  browser.execute_script("window.stop();")
                                  with open("left.txt", "a") as f:
                                                        f.write("\n")
                                                        f.write(href)                  
                                                
                            comments_page_html = browser.page_source
                            comments_page_soup = BeautifulSoup(comments_page_html, 'html.parser')
                            review = []
                            review_rating = []
                            
                            review = comments_page_soup.find_all('div', attrs={"itemprop": "review"})
                            
                           
                            for i in review:
                                review_rating_stars = []
                                review_rating_stars = i.find('div', class_="filled").find_all('span',class_="hg3-i hg3-i-star-full")
                                review_comment = i.find('div', class_="comment-text").text.encode('utf-8')
                                r = i.find('div', class_="commenter-info")
                                review_author = r.find('span', attrs={"itemprop": "author"}).text.encode('utf-8')
                                temp = review_author.split("in")
                                review_author_date = r.find('span', attrs={"itemprop": "datePublished"}).text.encode('utf-8')
                                if len(temp)> 1:   
                                    review_author_place = temp[1]                                    
                                else:
                                    review_author_place = "Unavailable"

                                doctor = [title,first_name, last_name,designation,  name,phone, workplace, addressLocality,addressRegion,  postalCode, rating_total_reviews, rating_total_comments, trustworthiness, explains_condition_well, answers_question, time_well_spent,
                                          schedulling, office_environment, staff_friendliness, average_Wait_Time, rating_total_stars,len(review_rating_stars),review_comment, review_author, review_author_place,review_author_date, board_certificates_one,
                                          board_certificates_one_accredited_by,board_certificates_two,board_certificates_two_accredited_by, board_certificates_three, board_certificates_three_accredited_by,
                                          education_one,education_type_one,education_year_one ,education_two,education_type_two,education_year_two,education_three,education_type_three,education_year_three ,
                                          admiting_privilidge_one, admiting_privilidge_streetAddress_one, admiting_privilidge_addressLocality_one,admiting_privilidge_addressRegion_one, admiting_privilidge_postalCode_one,
                                          admiting_privilidge_two, admiting_privilidge_streetAddress_two, admiting_privilidge_addressLocality_two,admiting_privilidge_addressRegion_two , admiting_privilidge_postalCode_two,num]
                                doctors.append(doctor)
     else:
                             
                            review = []
                            review_rating = []
                             
                            review = soup.find_all('div', class_="review")
                            if len(review) > 0:
                                for i in review:
                                    review_rating_stars = []
                                    review_rating_stars = i.find('div', class_="filled").find_all('span',class_="hg3-i hg3-i-star-full")
                                    review_comment = i.find('div', class_="comment-text").text.encode('utf-8')
                                    r = i.find('div', class_="commenter-info")
                                    review_author = r.find('span', attrs={"itemprop": "author"}).text.encode('utf-8')
                                    temp = review_author.split("in")
                                    review_author_date = r.find('span', attrs={"itemprop": "datePublished"}).text.encode('utf-8')
                                    if len(temp)>1:   
                                        review_author_place = temp[1]                                    
                                    else:
                                        review_author_place = "Unavailable"
                                    doctor = [title,first_name, last_name,designation,  name,phone, workplace, addressLocality,addressRegion,  postalCode, rating_total_reviews, rating_total_comments, trustworthiness, explains_condition_well, answers_question, time_well_spent,
                                          schedulling, office_environment, staff_friendliness, average_Wait_Time,rating_total_stars, len(review_rating_stars), review_comment, review_author, review_author_place,review_author_date, board_certificates_one,
                                          board_certificates_one_accredited_by,board_certificates_two,board_certificates_two_accredited_by, board_certificates_three, board_certificates_three_accredited_by,
                                              education_one,education_type_one,education_year_one ,education_two,education_type_two,education_year_two,education_three,education_type_three,education_year_three, admiting_privilidge_one, admiting_privilidge_streetAddress_one, admiting_privilidge_addressLocality_one,admiting_privilidge_addressRegion_one, admiting_privilidge_postalCode_one,
                                          admiting_privilidge_two, admiting_privilidge_streetAddress_two, admiting_privilidge_addressLocality_two,admiting_privilidge_addressRegion_two , admiting_privilidge_postalCode_two,num]
                                    doctors.append(doctor)
                            else:
                                    review_rating_stars = []
                                    review_comment = "Unavailable"
                                    review_author = "Unavailable"
                                    review_author_place ="Unavailable"
                                    review_author_date = "Unavailable"
                                    print "doctor", name
                                    doctor = [title,first_name, last_name,designation,  name,phone, workplace, addressLocality,addressRegion,  postalCode, rating_total_reviews, rating_total_comments, trustworthiness, explains_condition_well, answers_question, time_well_spent,
                                          schedulling, office_environment, staff_friendliness, average_Wait_Time, rating_total_stars,len(review_rating_stars), review_comment, review_author, review_author_place,review_author_date, board_certificates_one,
                                          board_certificates_one_accredited_by,board_certificates_two,board_certificates_two_accredited_by, board_certificates_three, board_certificates_three_accredited_by,
                                              education_one,education_type_one,education_year_one ,education_two,education_type_two,education_year_two,education_three,education_type_three,education_year_three ,
                                              admiting_privilidge_one, admiting_privilidge_streetAddress_one, admiting_privilidge_addressLocality_one,admiting_privilidge_addressRegion_one, admiting_privilidge_postalCode_one,
                                          admiting_privilidge_two, admiting_privilidge_streetAddress_two, admiting_privilidge_addressLocality_two,admiting_privilidge_addressRegion_two , admiting_privilidge_postalCode_two,num]

                                    doctors.append(doctor)

       
     return doctors

#This function is called for every pagination which in turn calls the method to fetch the data of the doctor in each row in every page.
def get_info(soup, num):
        doctor_lists = []
        doctor_list = soup.find_all("li", class_="uCard")
        for u in doctor_list:
            h3 = u.find('h3')
            if h3 is not None:
                        name = h3.find('a')
                        print "name in get_records", name                        
                        uniqueDocLink = name['href']
                        name = name.text.encode('utf-8')
                        name = name.strip()
                        print "name in get_records", name
                        record = get_doctor_details(uniqueDocLink, num)
                        for i in range(0, len(record)):
                            r = record[i]
                            doctor_lists.append(r)
        return doctor_lists


#This method is called for every page.
def get_records(num, state):
        print "Getting records  Inside get_records"
        print "PAGE NUMBER", num
        #while  name == "Loading":
        page = "https://www.healthgrades.com/usearch?what=Cardiology&entityCode=PS127&searchType=PracticingSpecialty&where=%s&pageNum=%d" % (state, num)
        try:
                browser.implicitly_wait(10) 
                browser.get(page)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                
                list = get_info(soup, num)
        except TimeoutException:
                print traceback.format_exc()
                browser.execute_script("window.stop();")
        return list   
    

    
#This function is called to print the data in an external CSV file.
def write_to_file(records,state):
    print "Inside writing to file method"
    with open('cardiothoracic_doctors_'+state+'.csv', 'a') as file:
        writer = csv.writer(file)
        for row in records:
            try:
                writer.writerow(row)
            except UnicodeError:
                print row
        



#This function returns the number of pages to perform pagination for each state.
def get_links(state):
            page = "https://www.healthgrades.com/usearch?what=Cardiology&entityCode=PS127&searchType=PracticingSpecialty&where=%s&pageNum=1" % state
            try:
                browser.implicitly_wait(10) 
                browser.get(page)
            except TimeoutException:
                print traceback.format_exc()
                browser.execute_script("window.stop();")
                with open("left.txt", "a") as f:
                    f.write("\n")
                    f.write(page)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            h1 = soup.find("h1", class_="uSearch-title")
            if h1 is not None:
                    h1 = h1.text.encode('utf-8')
                    a = h1.split(" ")
                    n = int(a[0]) / 20
                    if int(a[0])%20 != 0:
                        n = n+1
                    print "Number of pages", n
            return n    
                 
                   
        
def single_thread(state):
    n = get_links(state)
    for x in range(1,n+1):
         records = get_records(x, state)
         print "Writing to file"
         write_to_file(records,state) 
          


#Main function.
if __name__ == "__main__":

    print "Starting..."
    specialty = "cardiothoracic-surgeon"
    
    try:
        records = []
        states = get_states()
        for s in states:
	    print "Writing header to file method"
            heading = ["Title","First name", "Last name","Designation",  "Full name","Phone", "Workplace", "Address locality","Address region",  "Postal Code", "Total number of reviews", "Total number of comments", "trustworthiness", "explains_condition_well", "answers_question", "time_well_spent",
                                          "schedulling", "office_environment", "staff_friendliness", "average_Wait_Time", "Total rating value","Rating by patient", "Review comment by patient", "Patient name", "Patient place","Date of review", "board_certificates_one",
                                          "board_certificates_one_accredited_by","board_certificates_two","board_certificates_two_accredited_by", "board_certificates_three","board_certificates_three_accredited_by",
                                          "education_one","education_type_one","education_year_one" ,"education_two","education_type_two","education_year_two","education_three","education_type_three","education_year_three" ,
                                          "admiting_privilidge_one", "admiting_privilidge_streetAddress_one", "admiting_privilidge_addressLocality_one","admiting_privilidge_addressRegion_one", "admiting_privilidge_postalCode_one",
                                          "admiting_privilidge_two", "admiting_privilidge_streetAddress_two", "admiting_privilidge_addressLocality_two","admiting_privilidge_addressRegion_two" , "admiting_privilidge_postalCode_two","pageNum"]		
            with open('cardiothoracic_doctors_'+s+'.csv', 'a') as file:
		    writer = csv.writer(file)
		    try:
		        writer.writerow(heading)
		    except UnicodeError:
		            print row
            records = single_thread(s)
     
    finally:
        browser.service.process.send_signal(signal.SIGTERM)
        browser.quit()                               

#!/usr/bin/env python3
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import getpass
import re
import time
import sys
import traceback
import re

# custom modules
import userconfig as cfg

def scrape_user_data(netname, password):
    # HTML id/classes
    NETNAME_FIELD_ID = 'userid'
    PASSWORD_FIELD_ID = 'pwd'
    EMAIL_TEXT_ID = 'DERIVED_SSS_SCL_EMAIL_ADDR'
    IFRAME_ID = 'ptifrmtgtframe'
    SCHEDULE_BOX_ID = 'STDNT_WEEK_SCHD$scroll$0'
    PROGRAM_LINK_ID = 'DERIVED_SSS_SCL_SSS_MORE_ADVISOR$162$'
    PROGRAM_TEXT_ID = 'ACAD_PROG_TBL_DESCR$0'
    STUDENT_CENTER_LINK_ID = 'pthnavbccrefanc_HC_SSS_STUDENT_CENTER'
    DEMOGRAPHIC_DATA_LINK_ID = 'DERIVED_SSS_SCL_SS_DEMO_SUM_LINK'
    ID_LINK_ID = 'HCR_PERSON_I_EMPLID'
    NAME_LINK_ID = 'DERIVED_SSS_SCL_SS_NAMES_LINK'
    USER_NAME_CLASS = 'PSLEVEL1GRIDODDROW'

    # in seconds
    PAGE_LOAD_WAIT_TIME = 4

    # regexes
    course_code_rgx = re.compile('[A-Z]{4}\s\d{3,4}')
    timeslot_rgx = re.compile('')

    #@TODO: add usage string ?

    current_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
    chromedriver_path = current_dir + 'chromedriver'
    print('chromedriver_path: ', chromedriver_path)

    chrome_options = webdriver.ChromeOptions()
    # comment the next line to see what's actually happening
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no=sandbox") # required when running as root user. otherwise you would get no sandbox errors.
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')

    driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_options, service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])

    # directly go to student centre where most information is to be scraped from
    # after succesful login we should hit the 'Student Center' page
    #@TODO: this should be read from a property in a config file
    target_url = 'https://campus.concordia.ca/psp/pscsprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?'
    target_url_title = 'Student Center'

    driver.get(target_url)
    print('Page title: ', driver.title)

    netname = ''
    password = ''

    try:
        # get instances
        netname = driver.find_element_by_id(NETNAME_FIELD_ID)
        password = driver.find_element_by_id(PASSWORD_FIELD_ID)

        print('netname', netname)
        print('password', password)

    except Exception as err:
        print('Error encountered!')
        print(err)
        traceback.print_exc()

    print('Using netname:', user_netname)

    time.sleep(PAGE_LOAD_WAIT_TIME) # this line does not seem to help as it still flakes on the following line sometimes
    netname.clear()
    netname.send_keys(user_netname)
    password.clear()
    password.send_keys(user_password)
    password.send_keys(Keys.RETURN)

    elem = ''
    
    # begin building dictionary for user info
    user_info = {}
    # create a list of lists for each day of the week,
    # for all classes per day
    weekdays = [set() for i in range(5)]
    classes = []
    
    # check to see if login worked
    try:
        print('Reached page: ', driver.title)

        if target_url_title not in driver.title:
            print('Sign in failed, closing driver...')
            driver.close()
            print('exiting script')
            sys.exit()

        print('waiting for page to load for ' + str(PAGE_LOAD_WAIT_TIME) + ' seconds')
        time.sleep(PAGE_LOAD_WAIT_TIME)

        # start scraping for stuff on the current page
        print('locating user email address...')

        iframeContext = "return document.getElementById('" + IFRAME_ID + "').contentWindow.document"

        email = driver.execute_script(iframeContext + ".getElementById('" + EMAIL_TEXT_ID + "').innerHTML;")
        print('email', email)

        user_info['netname'] = user_netname
        user_info['email'] = email

        get_schedule_text = iframeContext + ".getElementById('" + SCHEDULE_BOX_ID + "').innerText"
        get_schedule_text += ".split('\\n').filter((value, index, array) => {return (value != null && !value.trim() == '')});"

        schedule = driver.execute_script(get_schedule_text)

        print('schedule', schedule)

        timeslots = []

        # to keep track of which day we last added to
        # so we can undo in case of 'ONLINE'
        last_day_added = 0

        for line in schedule:
            print('processing: ', line)
            if course_code_rgx.match(line):
                print('found course')
                if '-' in line:
                    classes.append(line.split('-')[0])
                    print('course added')
                else:
                    classes.append(line)
                    print('course added')
            if timeslot_rgx.match(line):
                if len(classes) > 0:
                    days = re.search('[A-Za-z]{2,4}', line).group(0)
                    timeslot = ',' + line.replace(days + ' ', '')

                    if 'Mo' in line:
                        weekdays[0].add(classes[-1] + timeslot)
                        last_day_added = 0
                        print('Mo')
                    if 'Tu' in line:
                        weekdays[1].add(classes[-1] + timeslot)
                        last_day_added = 1
                        print('Tu')
                    if 'We' in line:
                        weekdays[2].add(classes[-1] + timeslot)
                        last_day_added = 2
                        print('We')
                    if 'Th' in line:
                        weekdays[3].add(classes[-1] + timeslot)
                        last_day_added = 3
                        print('Th')
                    if 'Fr' in line:
                        weekdays[4].add(classes[-1] + timeslot)
                        last_day_added = 4
                        print('Fr')

        # remove duplicates
        classes = list(set(classes))

        # convert back to list of lists to be more easily JSON-ified
        weekdays = [list(x) for x in weekdays]

        # navigate to page containing program
        program_link_click = iframeContext + ".getElementById('" + PROGRAM_LINK_ID + "').click()"
        driver.execute_script(program_link_click)

        time.sleep(PAGE_LOAD_WAIT_TIME)

        print('Page title: ', driver.title)

        if driver.title == "My Advisors":
            print('Sucessfuly changed to My Advisors page')
        else:
            print('Failed to change to My Advisors page')
            sys.exit(0)

        # add academic program
        get_user_program = iframeContext + ".getElementById('" + PROGRAM_TEXT_ID + "').innerText"
        user_program = driver.execute_script(get_user_program)
        print('program', user_program)
        user_info['program'] = user_program

        click_student_center = "document.getElementById('" + STUDENT_CENTER_LINK_ID + "').click()"
        # go back home so we can retrieve the id
        driver.execute_script(click_student_center)
        time.sleep(PAGE_LOAD_WAIT_TIME)

        if driver.title == "Student Center":
            print('Sucessfuly changed to Student Center page')
        else:
            print('Failed to change to Student Center page (0)')
            sys.exit(0)

        click_demographic_data = iframeContext + ".getElementById('" + DEMOGRAPHIC_DATA_LINK_ID + "').click()"
        driver.execute_script(click_demographic_data)
        time.sleep(PAGE_LOAD_WAIT_TIME)

        if driver.title == "Demographic Information":
            print('Sucessfuly changed to Demographic Information page')
        else:
            print('Failed to change to Demographic Information page')
            sys.exit(0)

        get_user_id = iframeContext + ".getElementById('" + ID_LINK_ID + "').innerText"
        user_id = driver.execute_script(get_user_id)
        print('user_id:', user_id)

        user_info['id'] = user_id

        driver.execute_script(click_student_center)
        time.sleep(PAGE_LOAD_WAIT_TIME)

        if driver.title == "Student Center":
            print('Sucessfuly changed to Student Center page')
        else:
            print('Failed to change to Student Center page (1)')
            sys.exit(0)

        click_names = iframeContext + ".getElementById('" + NAME_LINK_ID + "').click()"
        driver.execute_script(click_names)
        time.sleep(PAGE_LOAD_WAIT_TIME)

        if driver.title == "Names":
            print('Sucessfuly changed to Names page')
        else:
            print('Failed to change to Names page')
            sys.exit(0)

        get_user_name = iframeContext + ".getElementsByClassName('" + USER_NAME_CLASS +"')[1].innerText"
        user_name = driver.execute_script(get_user_name)
        user_info['name'] = user_name

    except Exception as err:
        print('Error encountered!')
        print(err)
        traceback.print_exc()

    finally:
        # print final feedback
        print('user_info', user_info)
        print('classes', classes)
        print('weekdays', weekdays)

        # close it up
        print('closing driver...')
        driver.close()
        print('driver closed')

        return (user_info, weekdays)

if __name__ == "__main__":
    # check if userconfig has netname + password set, use it if so
    if cfg.user['netname'] and cfg.user['password']:
        print('Using user config set in userconfig.py')
        user_netname = cfg.user['netname']
        user_password = cfg.user['password']
    else:
        # if credentials not on file, then have user input them
        print('Config file either missing user, password, or both')
        print('Enter netname: ')
        user_netname = input()

        user_password = getpass.getpass('Enter password: ')

    thing = scrape_user_data(user_netname, user_password)
    print('thing', thing)

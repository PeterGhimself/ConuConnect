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

new_branch_name = 'testy'
# in case multiple branch names passed at once
new_branch_names = []

# if passing multiple branch names then as a single string
# with comma separated values and no spaces
MULTI_ARG_DELIMETER = ','

# list option variables
list_branches = False
LIST_FLAGS = ['--list', '-l']
## user feedback messages
UPDATE_MODE_MSG = 'Update mode selected'
LIST_MODE_MSG = 'List mode selected'
LIST_FLAG_TYPO_MSG = 'Did you mean --list or -l? '
EXIT_PROMPT = 'q to quit now '
USER_INPUT_OPTIONS = '(y/n/q): '
EXIT_OPTION_MSG = 'Exiting script'

# file meant to keep track of the latest branch values
# gets overwritten very time branches are updated/listed
BRANCH_LIST_FILE = 'updated_branch_list'

# HTML id/classes
NETNAME_FIELD_ID = 'userid'
PASSWORD_FIELD_ID = 'pwd'
EMAIL_TEXT_ID = 'DERIVED_SSS_SCL_EMAIL_ADDR'
IFRAME_ID = 'ptifrmtgtframe'
SCHEDULE_BOX_ID = 'STDNT_WEEK_SCHD$scroll$0'
# in seconds
PAGE_LOAD_WAIT_TIME = 5

# regexes
course_code_rgx = re.compile('[A-Z]{4}\s\d{3,4}')
timeslot_rgx = re.compile('')

#@TODO: add usage string

if len(sys.argv) > 1:
    new_branch_name = sys.argv[1]

    if new_branch_name in LIST_FLAGS:
        list_branches = True
        print(LIST_MODE_MSG)
    # try to catch typos
    elif 'list' in new_branch_name:
        answer = input(LIST_FLAG_TYPO_MSG + '\n' + EXIT_PROMPT + USER_INPUT_OPTIONS)
        if answer.lower() == 'y':
            list_branches = True
            print(LIST_MODE_MSG)
        elif answer.lower() == 'q':
            print(EXIT_OPTION_MSG)
            sys.exit(0)
        else:
            print(UPDATE_MODE_MSG)
    else:
        # check if multiple branch names
        if MULTI_ARG_DELIMETER in new_branch_name:
            print('Multiple branch names detected')
            new_branch_names = new_branch_name.split(MULTI_ARG_DELIMETER)
            # remove duplicates
            new_branch_names = list(dict.fromkeys(new_branch_names))

            for branch in new_branch_names:
                print("Found: " + branch)

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

except Exception as err:
    print('Error encountered!')
    print(err)
    traceback.print_exc()

# check config file
if cfg.user['netname'] and cfg.user['password']:
    print('Using user config set in userconfig.py')
    user_netname = cfg.user['netname']
    user_password = cfg.user['password']

    print('Using netname:', user_netname)

    print('netname:', netname)

    # wait just a bit, otherwise line below is flaky
    #@TODO: do a real fix for the netname.clear() bug
    time.sleep(3) # this line does not seem to help as it still flakes on the following line sometimes
    netname.clear()
    netname.send_keys(user_netname)
    password.clear()
    password.send_keys(user_password)
    password.send_keys(Keys.RETURN)

else:
    # if credentials not on file, then have user input them
    print('Config file either missing user, password, or both')
    print('Enter netname: ')
    user_netname = input()

    netname.clear()
    netname.send_keys(user_netname)

    user_password = getpass.getpass('Enter password: ')

    password.clear()
    password.send_keys(user_password)
    password.send_keys(Keys.RETURN)

elem = ''

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

    # being building dictionary for user info
    user_info = {}

    iframeContext = "return document.getElementById('" + IFRAME_ID + "').contentWindow.document"

    email = driver.execute_script(iframeContext + ".getElementById('" + EMAIL_TEXT_ID + "').innerHTML;")
    print('email', email)

    user_info['netname'] = user_netname
    user_info['email'] = email
   
    schedule_query = iframeContext + ".getElementById('" + SCHEDULE_BOX_ID + "').innerText"
    schedule_query += ".split('\\n').filter((value, index, array) => {return (value != null && !value.trim() == '')});"

    #print('schedule_query', schedule_query)

    schedule = driver.execute_script(schedule_query)
    
    print('schedule', schedule)

    # create a list of lists for each day of the week,
    # for all classes per day
    weekdays = [set() for i in range(5)]
    classes = []
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

    print('classes', classes)
    print('weekdays', weekdays)

    # navigate to page containing program
    program_link_click = iframeContext + ".getElementById('DERIVED_SSS_SCL_SSS_MORE_ADVISOR$162$').click()"
    driver.execute_script(program_link_click)

    time.sleep(5)

    print('Page title: ', driver.title)
    
    if driver.title == "My Advisors":
        print('Sucessfuly changed to My Advisors page')
    else:
        print('Failed to change to My Advisors page')
        sys.exit(0)

    # add academic program
    get_user_program = iframeContext + ".getElementById('ACAD_PROG_TBL_DESCR$0').innerText"
    user_program = driver.execute_script(get_user_program)
    print('program', user_program)
    user_info['program'] = user_program
    
    print('user_info', user_info)

    driver.close()
    sys.exit()

    # so let's try javscripting this instead
    print('inserting value: ', new_branch_name)
    #TODO: try to implement it properly as shown in 'get_branch_list.js' vs this hack
    branches_val = "document.getElementsByName('branches[]')[2].value"

    
    if list_branches:
        get_branches = 'return ' + branches_val 
        branch_list = driver.execute_script(get_branches)
        print('listing current branches:')
        print(branch_list)

        # save list to file
        with open(BRANCH_LIST_FILE, 'w+') as f:
            f.write(branch_list + "\n")

    else:
        # for the TODO fix mentioned above
        """branches_val = ''
        with open('./get_branch_list.js', 'r') as js:
            # 3) Read the jquery from a file
            branches_val = js.read()

        get_branches = "return " + branches_val
        updated_branch_list = driver.execute_script(get_branches)

        # visual confirmation
        print('updated branch list: ', updated_branch_list)
        """
        set_branches = branches_val + " += '"
        if len(new_branch_names) > 0:
            for branch in new_branch_names:
                set_branches += ', ' + branch
            set_branches += "'"
        else:
            set_branches = branches_val + " += ', " + new_branch_name + "'"
        print('set_branches', set_branches)
        get_branches = "return " + branches_val
        driver.execute_script(set_branches)
        updated_branch_list = driver.execute_script(get_branches)

        # visual confirmation
        print('updated branch list: ', updated_branch_list)

        # save list to file
        with open(BRANCH_LIST_FILE, 'w+') as f:
            f.write(updated_branch_list + "\n")

        # necessary wait, otherwise save button gets clicked too fast to actually work
        time.sleep(0.5)

        # only parent is clickable with selenium driver
        # although in js child is clickable
        print('locating save button...')
        save = driver.find_element_by_id('add_integration_parent')
        save.click()

except Exception as err:
    print('Error encountered!')
    print(err)
    traceback.print_exc()

print('closing driver...')
driver.close()
print('driver closed')

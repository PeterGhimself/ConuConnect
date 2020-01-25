#!/usr/bin/env python3
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import getpass
import re
import time
import sys
import traceback
import userconfig as cfg

# set default name if none passed in args
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

#@TODO: add usage string
#@TODO: search and replace (given an empty string to replace with, delete that entry)

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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no=sandbox") # required when running as root user. otherwise you would get no sandbox errors.

driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_options, service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])

# directly go to github enterprise server integration settings page, which will first redirect to login page
# after succesful login we should hit the 'Github Enterprise Server | Slack App Directory' page
#@TODO: this should be read from a property in a config file
target_url = 'https://spaceconcordiateam.slack.com/services/B2ZGUM4MV'

driver.get(target_url)
print('Page title: ', driver.title)

email = ''
password = ''

try:
    # get instances
    email = driver.find_element_by_id('email')
    password = driver.find_element_by_id('password')

except Exception as err:
    print('Error encountered!')
    print(err)
    traceback.print_exc()

# check config file
if cfg.user['email'] and cfg.user['password']:
    print('Using user config set in slackconfig.py')
    user_email = cfg.user['email']
    user_password = cfg.user['password']

    print('Using email:', user_email)

    email.clear()
    email.send_keys(user_email)
    password.clear()
    password.send_keys(user_password)
    password.send_keys(Keys.RETURN)

else:
    print('Config file either missing user, password, or both')
    print('Enter email: ')
    user_email = input()

    email.clear()
    email.send_keys(user_email)

    user_password = getpass.getpass('Enter password: ')

    password.clear()
    password.send_keys(user_password)
    password.send_keys(Keys.RETURN)

elem = ''

# check to see if login worked
try:
    print('Login success, on page: ', driver.title)

    if 'GitHub Enterprise Server | Slack App Directory' not in driver.title:
        print('Sign in failed, closing driver...')
        driver.close()
        print('exiting script')
        sys.exit()

    '''
    # One way of checking the page source for matches
    src = driver.page_source
    text_found = re.search(r'class="branches small"', src)
    print('text_found', text_found)
    '''

    # append branch name to branch list
    print('locating branches...')

    # this method doesn't seem to be working
    #branch_list = driver.find_element_by_class_name('branches')
    #branch_list.send_keys(', test!')

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

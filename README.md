# ConuConnect
A smart calendar app for allowing Concordia students to easily discover other students who have similar breaks, with options to filter by.

## MVP

### Features

- Sign-on / auth via myconcordia credentials
- Get schedule via myconcordia credentials
- Ask user to enter leeway times for before their first class / after their last class
- [Secondary] Ask user to enter list of student IDs a.k.a 'friends list'
  - Student 'friend' discovery by name search
- Display the user's schedule
- For a given break, allow user to list other students with the same break
  - Support filtering by the following criteria:
    - Specific program(s) e.g. computer science, software eng   
    - Specific subject(s) e.g. COMP, ENCS, MATH
    - Specific course(s) e.g. COMP 248, ENGR 233
    - Shares common course(s)
    - Same course immediately before/after break
    - Specific person(s)
  - Support ranking by the following criteria:
    - Program similarity composite score (common courses / same program)
    - Break overlap percentage
    - Specific person(s) / friends

### Extraz

- Get matches list based off a given week
- Filters:
  - Specific department(s) e.g. engineering, arts, jmsb
- Rankings:
  - asdfsd
- Granular control over leeway times
- Aggregated heatmap of break times for a given student profile
- Tntegration with contacts application for friend discovery
- Mobile support

### Legend

- [Secondary] --> Backend feature should be done but minimal UI implementation

## Cloning

Make sure to run `git update-index --skip-worktree userconfig.py` after cloning to ensure that the changes to the config file won't be tracked.

## Dependencies/Setup

The scripts are developed/tested with Python 3.6.8.

### Linux (currently only supported option)

It is suggested to use a virtual environment, as the `selenium` package is needed.

1. Create a new virtual environment with: ```virtualenv -p `which python3.6` venv```, activate it with `. venv/bin/activate`. You should see `(venv)` prepended to your `user@hostname`.

2. With your venv activated, install python packages in `requirements.txt`: `pip install -r requirements.txt`

3. Download ChromeDriver and copy to the root of this repo. If you want this script to run it has to be in the same folder as the `chromedriver` executable. Instructions originally found [here](https://blog.testproject.io/2018/02/20/chrome-headless-selenium-python-linux-servers/), how to get chromedriver summarized below.

```
cd /path/to/ConuConnect
wget https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
```


# ConuConnect
A smart calendar app for allowing Concordia students to easily discover other students who have similar breaks, with options to filter by.

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


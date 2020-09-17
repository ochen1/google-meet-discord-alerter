import os
from time import sleep

from assertGoogleLogin import assertLogin
from selenium import webdriver
from traceback import print_exc
from os.path import dirname, abspath

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
chrome_options.add_argument(
    "--user-data-dir=" + os.path.abspath(os.getenv('VPROF_PATH')))
chrome_options.binary_location = os.getenv('GOOGLE_CHROME_PATH')
if os.getenv('PROXY'):
    chrome_options.add_argument(f"--proxy-server={os.getenv('PROXY')}")


def getNumPeople(mid):
    try:
        driver = webdriver.Chrome(
            executable_path=os.getenv('CHROMEDRIVER_PATH'),
            options=chrome_options
        )
        try:
            assertLogin(driver)
        except AssertionError:
            return '[error]'
        driver.get("https://meet.google.com/lookup/%s" % mid)
        sleep(2)
        v = driver.execute_script("""
    if (document.querySelector('.U04fid') != null) {    
        if (document.querySelector('.U04fid').children.length > 3) {
            return (parseInt(document.getElementsByClassName('w5wUXb')[0].innerText) + document.querySelector('.U04fid').children.length - 1);
        } else {
            return document.querySelector('.U04fid').children.length;
        }
    } else {
        return 1;
    }
    """)
    except Exception:
        with open(dirname(abspath(__file__)).rstrip('/') + '/logs.log', 'a') as logf:
            print_exc(file=logf)
        v = '[error]'
    finally:
        try:
            driver.close()
        except:
            pass
    return v

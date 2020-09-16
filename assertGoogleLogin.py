from os import getenv
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys


def assertLogin(d: WebDriver):
    d.get("https://myaccount.google.com/")
    sleep(0.4)
    if "myaccount.google.com" in d.current_url:
        d.find_element_by_xpath(
            "/html/body/div[2]/header/div[2]/div[3]/div[1]/div/div/a").click()
        sleep(0.1)
        if d.execute_script(
                "return (document.querySelector('.gb_sb').innerText == \"%s\" ? true : false)" % getenv('GEMAIL')):
            return
        else:
            d.get("https://accounts.google.com/Logout")
            sleep(1)
            pass
    else:
        pass
    d.get('https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow')
    sleep(1)
    d.execute_script("""
for (li of document.querySelector('.OVnw0d').children) {
    if (li.innerText == "Use another account") {
        li.children[0].click();
    }
}
""")
    sleep(1)
    d.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input").send_keys(getenv('GEMAIL'))
    d.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input").send_keys(Keys.RETURN)
    sleep(2)
    d.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input").send_keys(getenv('GPASS'))
    d.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input").send_keys(Keys.RETURN)
    sleep(2)
    assert "developers.google.com/oauthplayground" in d.current_url

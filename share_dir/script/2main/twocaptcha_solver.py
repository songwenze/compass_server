import random
import time
import traceback

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import compass_byerecaptcha
import main
from conf import FIREFOX_PROFILE_PATH, DRIVER_PATH


class ReCaptchaServiceError(Exception):
    """Base class for other exceptions"""
    pass


class ChannelError(Exception):
    """Base class for other exceptions"""
    pass

def solver_2recaptcha(browser, page_url, max_wait=30):
    recaptchaFrame = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))

    site_key_element = browser.find_element_by_css_selector('[data-sitekey]')

    site_key = site_key_element.get_attribute("data-sitekey")
    method = "userrecaptcha"
    key = "07ffe5490594d31c638e9196b0dbc11f"

    url = "http://2captcha.com/in.php?key={}&method={}&googlekey={}&pageurl={}".format(key, method, site_key, page_url)
    response = requests.get(url)

    if response.text[0:2] != 'OK':
        print('Service error. Error code:' + response.text)

    captcha_id = response.text[3:]

    token_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(key, captcha_id)

    retry_time = 0
    while True:
        retry_time += 1
        print("retry times", retry_time)
        if retry_time > max_wait:
            raise Exception("2captcha wait too long, failed")
        time.sleep(3)
        response = requests.get(token_url)
        if response.text[0:2] == 'OK':
            break

    captha_results = response.text[3:]
    try:
        browser.execute_script(
        """document.getElementById("g-recaptcha-response").innerHTML = arguments[0]""", captha_results)
    except JavascriptException as e:
        # print(browser.page_source)
        traceback.print_exc()
        raise e





    # browser.find_element_by_id("g-recaptcha-response").submit()
    # browser.find_element_by_css_selector('[id="recaptcha-demo-submit"]').click()

def pre_operation(browser, url, refresh=False):
    if refresh:
        browser.refresh()
    else:
        browser.get(url)
    browser.execute_script("window.scrollBy(0, window.innerHeight * 1.5 )")



    try:
        browser.find_element(By.CSS_SELECTOR, '[aria-label="View email address"]').click()
        return
    except NoSuchElementException:
        pass
    except Exception:
        traceback.print_exc()

    time.sleep(2000)
    if 'For business inquiries:' not in browser.page_source:
        print('no email for channel ')
        raise ChannelError()
    try:
        browser.find_element(By.CSS_SELECTOR, '#details-container yt-button-shape').click()
        return
    except Exception as e:
        raise e

def check_proxy(account):
    chrome_driver = "/Users/songwenze/Downloads/geckodriver"
    profile = webdriver.FirefoxProfile(f"""/opt/data/shm/{account}/""")

    # 无法应用带密码的proxy
    # profile.set_preference("network.proxy.type", 1)
    # profile.set_preference('network.proxy.ssl_port', 2333)
    # profile.set_preference('network.proxy.ssl', '156.234.51.213')
    # profile.set_preference("network.proxy.http", '156.234.51.213')
    # profile.set_preference("network.proxy.http_port", 2333)
    # profile.set_preference("network.proxy.username", 'okg1234')
    # profile.set_preference("network.proxy.password", 'pkKonrEs')
    from selenium.webdriver import FirefoxOptions

    options = FirefoxOptions()
    browser = webdriver.Firefox(executable_path=chrome_driver, firefox_profile=profile, options=options)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(10)
    browser.set_script_timeout(10)
    browser.get("about:preferences")
    browser.find_element_by_css_selector("#connectionSettings").click()
    browser.switch_to.frame(1)
    time.sleep(1)
    proxy_elm = browser.find_element_by_css_selector("#networkProxyHTTP").get_attribute("value")
    # if len(proxy_elm) > 0:
    print(account, proxy_elm)
    browser.quit()

def v2_make_randome_actions(driver, watch_time=300):
    driver.get('''https://www.youtube.com/user/cs12345679/videos''')

    time.sleep(3)
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#buttons #subscribe-button")))
    print(element.text)
    if 'Subscribed' != element.text:
        element.click()

    video = driver.find_elements_by_class_name('ytd-rich-grid-row #content.ytd-rich-item-renderer')
    random.choice(video).click()
    # video[3].click()
    time.sleep(random.randint(1, 6))
    driver.execute_script("window.scrollBy(0, 500)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 1000)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, -1000)")
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#segmented-like-button')))
    like_pressed = driver.find_element_by_css_selector('#top-row #segmented-like-button button[aria-pressed]').get_attribute('aria-pressed')
    print(like_pressed)
    if "false" == like_pressed:
        element.click()
    time.sleep(random.randint(1, 5))




def make_randome_actions(driver, watch_time=300):
    driver.get(f'''https://www.youtube.com/''')
    time.sleep(3)
    video = driver.find_elements_by_class_name('ytd-rich-grid-row #content.ytd-rich-item-renderer')
    # random.choice(video).click()
    random.choice(video).click()
    time.sleep(random.randint(1, 6))
    driver.execute_script("window.scrollBy(0, 500)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 1000)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, -1000)")
    time.sleep(random.randint(3, 30))

def human_fake_action(account):
    chrome_driver = DRIVER_PATH
    profile = webdriver.FirefoxProfile(f"""{FIREFOX_PROFILE_PATH}/{account}/""")
    from selenium.webdriver import FirefoxOptions

    options = FirefoxOptions()
    options.add_argument('--allow-downgrade')
    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("useAutomationExtension", False)
    # options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Firefox(executable_path=chrome_driver, firefox_profile=profile, options=options)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(10)
    browser.set_script_timeout(10)
    try:
        v2_make_randome_actions(browser)
        make_randome_actions(browser)
    except:
        traceback.print_exc()
    finally:
        if '''Email address hidden. You've reached today's access limit.''' in browser.page_source:
            browser.quit()
            raise Exception('reached access limit')
        browser.quit()

def main_solve(url, account):
    chrome_driver = DRIVER_PATH
    profile = webdriver.FirefoxProfile(f"""{FIREFOX_PROFILE_PATH}/{account}/""")

    # 无法应用带密码的proxy
    # profile.set_preference("network.proxy.type", 1)
    # profile.set_preference('network.proxy.ssl_port', 2333)
    # profile.set_preference('network.proxy.ssl', '156.234.51.213')
    # profile.set_preference("network.proxy.http", '156.234.51.213')
    # profile.set_preference("network.proxy.http_port", 2333)
    # profile.set_preference("network.proxy.username", 'okg1234')
    # profile.set_preference("network.proxy.password", 'pkKonrEs')
    from selenium.webdriver import FirefoxOptions

    options = FirefoxOptions()
    options.add_argument('--allow-downgrade')
    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("useAutomationExtension", False)
    # options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Firefox(executable_path=chrome_driver, firefox_profile=profile, options=options)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(10)
    browser.set_script_timeout(10)
    email = None
    recaptcha_error = False
    try:
        time_start = time.time()
        # make_randome_actions(browser, 10)
        try:
            pre_operation(browser, url)
        except ChannelError as e:
            raise e
        except:
            pre_operation(browser, url, refresh=True)
        try:
            solver_2recaptcha(browser, url)
            # compass_byerecaptcha.solveRecaptcha(browser)
        except:
            pre_operation(browser, url, refresh=False)
            # solver_2recaptcha(browser, url)
            # return

            # if modeling failed, use 2recaptcha instead
            # pre_operation(browser, url, refresh=True)
            # solver_2recaptcha(browser, url)


        element = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit-btn")))
        browser.execute_script('arguments[0].click()', element)
        # element.click()

        for i in range(1, 4):
            time.sleep(3)
            email = browser.find_element(By.CSS_SELECTOR, '#email.ytd-channel-about-metadata-renderer').text
            if email is not None and not email.strip():
                break
            try:
                element.click()
            except ElementNotInteractableException:
                time.sleep(3)
                email = browser.find_element(By.CSS_SELECTOR, '#email.ytd-channel-about-metadata-renderer').text
                break
        if email is None or not email.strip():
            raise ReCaptchaServiceError()
    except:
        traceback.print_exc()
        raise
    finally:
        if '''Email address hidden. You've reached today's access limit.''' in browser.page_source:
            browser.quit()
            raise Exception('reached access limit')
        browser.quit()
    time_end = time.time()
    print('time cost', time_end - time_start, 's')
    print("email: ", email)
    return email

if __name__ == '__main__':
    chrome_driver = "/Users/songwenze/Downloads/geckodriver"


    # 无法应用带密码的proxy
    # profile.set_preference("network.proxy.type", 1)
    # profile.set_preference('network.proxy.ssl_port', 2333)
    # profile.set_preference('network.proxy.ssl', '156.234.51.213')
    # profile.set_preference("network.proxy.http", '156.234.51.213')
    # profile.set_preference("network.proxy.http_port", 2333)
    # profile.set_preference("network.proxy.username", 'okg1234')
    # profile.set_preference("network.proxy.password", 'pkKonrEs')
    from selenium.webdriver import FirefoxOptions

    mysql_db = main.get_mysql_connect()
    start = True
    for account in [e[0] for e in main.query_all_accounts(mysql_db)]:
        profile = webdriver.FirefoxProfile(f"""/opt/data/shm/{account}/""")
        print(account)
        options = FirefoxOptions()
        options.add_argument('--allow-downgrade')
        # options.set_preference("dom.webdriver.enabled", False)
        # options.set_preference("useAutomationExtension", False)
        # options.add_argument("--disable-blink-features=AutomationControlled")
        browser = webdriver.Firefox(executable_path=chrome_driver, firefox_profile=profile, options=options)
        browser.implicitly_wait(10)
        browser.set_page_load_timeout(10)
        browser.set_script_timeout(10)
        try:
            v2_make_randome_actions(browser)
        except:
            traceback.print_exc()
            browser.refresh()
            v2_make_randome_actions(browser)
        browser.quit()
    # main_solve("https://www.youtube.com/channel/UCFksyaxavi6p_KMeuyZAWUA/about", "account01")

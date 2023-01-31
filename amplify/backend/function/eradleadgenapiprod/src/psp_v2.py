import requests
import re
from chrome_headless import driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


already_checked_pages = []
urls = {
    'link': "",
    'original_url': "",
    'current_url': ""
}

def close_driver():
    driver.quit()
def check_include_stripe():
    res = False
    current_state = "checked"
    resultsStripe = driver.find_elements(
        By.XPATH, "//*[contains(@id, 'stripe')]")
    resultsTap = driver.find_elements(
        By.XPATH, "//*[contains(@id, 'payment_method_tap')]")
    if (len(resultsStripe)):
        current_state = 'Stripe'
        res = True
    if (len(resultsTap)):
        current_state = 'Tap'
        res = True
    return [res, current_state]


def check_keyword(a_tags, case_scenario_1_start):
    res = False
    href = ""
    for a in a_tags:
        text = clean_text(a.text)
        if (text in case_scenario_1_start):
            href = a['href']
            res = True
            break
    if res == True:
        return href
    else:
        return False


def clean_text(text):
    if(type(text) is str):
        return text.strip().lower()
    return text


def text_match(original_text, match_text, match_type):
    # type = 1 exact match
    # type = 2 starts with
    # type = 3 include
    res = False
    if(type(original_text) is str):
        text = clean_text(original_text)
        no_space = text.replace(" ", "")
        if (len(no_space) > 0):
            if (match_type == 1 and text == match_text):
                res = True
            elif (match_type == 2 and text.startswith(match_text)):
                res = True
            elif (match_type == 3 and match_text in text):
                if ('test' in text):
                    res = False
                else:
                    res = True
    return res


def text_not_match(original_text, match_text):
    res = False
    if(type(original_text) is str):
        text = clean_text(original_text)
        no_space = text.replace(" ", "")
        if (len(no_space) > 0):
            if (match_text in text):
                res = True
    return res


def build_link_form_href(href, currentUrl):
    url = href
    if 'https' in url:
        url = url
    else:
        url = currentUrl + url
    return url


def buttons_check(buttons_with_select, match_text, match_type):
    res = False
    try:
        for button in buttons_with_select:
            if (text_match(button.text, match_text, match_type)):
                driver.find_element(
                    By.CLASS_NAME, button['class'][0]).click()
                content = driver.page_source
                res = True
                break
    except (NoSuchElementException, InvalidArgumentException, ElementNotInteractableException):
        res = False
        print('ERROR: Add to cart BUTTON not found or not clickable at this point')
    except ElementClickInterceptedException:
        WebDriverWait(driver, 5)
        res = buttons_check(buttons_with_select, match_text, match_type)
    except UnexpectedAlertPresentException:
        # Select option if required
        try: 
            x = driver.find_element(By.ID, 'size')
            drop = Select(x)
            drop.select_by_index(2)
            print('ERROR: Item selecting option')
            res = buttons_check(buttons_with_select, match_text, match_type)
        except: 
            res = buttons_check(buttons_with_select, match_text, match_type)
            print('error #132')
    return res


def links_check(a_with_select, match_text, match_type):
    res = False
    for a in a_with_select:
        if (text_match(a.text, match_text, match_type)):
            try:
                length_a_href = len(a['href'])
                l = a['href']
            except KeyError:
                length_a_href = 0
            if (length_a_href > 0 and text_not_match(length_a_href, 'javascript') == False):
                go = build_link_form_href(l, urls['current_url'])
                print('#125 Redirecting to:' + go)
                res = True
                driver.get(go)
                break
    return res


def links_check_by_href(a_with_select, match_text, match_type):
    res = False
    try:
        for a in a_with_select:
            if (text_match(a['href'], match_text, match_type) and text_not_match(a['href'], 'card') == False):
                if (len(a['href']) > 0):
                    go = build_link_form_href(a['href'], urls['original_url'])
                    print('#204 Redirecting to:' + go)
                    res = True
                    driver.get(go)
                    break
    except KeyError:
        res = res
    return res


def checked_custom_case_1():
    res = False
    content = driver.page_source
    a_with_select = re.findall(r'<a.*?>.*?<\/a>', content)
    for a in a_with_select:
        match = re.search(r'buy now', a)
        if match:
            match = re.search(r'href="(.*?)"', a)
            if match:
                link = match.group(1)
                go = build_link_form_href(link, urls['original_url'])
                print('#233 Redirecting to:' + go)
                res = True
                driver.get(go)
                break
    return res   

def add_to_cards(a_with_select, match_text, match_type):
    res = False
    for a in a_with_select:
        if (text_match(a.text, match_text, match_type)):
            res = True
            break
    return res


def check_proceed_checkout_page():
    res = False
    content = driver.page_source
    link_tag_found = False
    a_tags = re.findall(r'<a.*?>.*?</a>', content)
    button_tags = re.findall(r'<button.*?>.*?</button>', content)
    
    for a_tag in a_tags:
        if re.search(r'proceed checkout|place order|proceed to checkout', a_tag, re.IGNORECASE):
            link_tag_found = True
            break
    
    if link_tag_found:
        res = True
    else:
        for button_tag in button_tags:
            if re.search(r'proceed', button_tag, re.IGNORECASE):
                res = True
                break
                
    return res


def check_view_cart_and_checkout(a_tags):
    # TO DO will add form filling function here
    res = False
    link_found = links_check(a_tags, 'checkout', 2)
    if (link_found == False):
        link_found = links_check(a_tags, 'check out', 2)
    if(link_found):
        res = True
    return res


def check_url(url):
    res = False
    response = requests.get(url)
    print(response.status_code)
    status_code = response.status_code
    if (status_code >= 200 and status_code < 300 or status_code in [403, 406]):
        res = True
    return res


def detect_type_of_website(title, link):
    # type = 1 general
    # type = 2 flight booking www.eilago.com
    # type = 3 ticket booking
    # type = 4 travel package adrenaline-travel.com/
    type = 1
    for t in title:
        check_title = clean_text(t.text)
        if ('book' in check_title and 'flight' in check_title):
            type = 2
        if ('travel' in check_title and 'travel' in link):
            type = 4
    return type

#  -------------------------  MAIN FUNCTION STARTS FROM HERE ------------------------------


def find_psp(link):
    current_state = '-'
    continue_step = True
    already_checked_pages.clear()
    original_url = 'https://'+link
    urls['link'] = link
    urls['original_url'] = original_url
    urls['current_url'] = original_url
    
    already_checked_pages.append(original_url)
    print("----------------------------------")
    print(original_url)

    try:
        if (check_url(original_url)):
            driver.get(original_url)
        else:
            current_state = 'Error loading the page #starting point'
            continue_step = False
    except Exception as e:
        continue_step = False
        if(e.__class__.__name__ == 'MaxRetryError'):
            current_state = "Blocked"
        else: 
            current_state = "Error loading page"
        print("except -> driver.get -> %s" % e)

    if (continue_step):

        content_home_page = driver.page_source
        title = re.findall(r'<title>(.+?)</title>', content_home_page)

        type_of_website = detect_type_of_website(title, link)

        if (type_of_website == 1):
            tmp_state_checker = check_include_stripe()
            if (tmp_state_checker[0] == False):
                currentUrl = original_url
                urls['current_url'] = currentUrl
                a_tags_home = re.findall(r'<a(.*?)>', content_home_page)

                add_to_cart_found = False
                found_psp = False

                case_scenario_1_start = [
                    'shop', 'shop now', 'view more', 'buy']
                case_scenario_1 = False
                case_cart_access = False

                while True:
                    content_tmp = driver.page_source
                    a_tags_tmp = re.findall(r'<a(.*?)>', content_tmp)

                    visit_link = ""
                    # Find starting point
                    res = check_keyword(a_tags_tmp, case_scenario_1_start)
                    if (res != False):
                        case_scenario_1 = True
                        visit_link = res

                    if (case_scenario_1):
                        if 'http' in visit_link:
                            currentUrl = visit_link
                        else:
                            currentUrl = original_url + visit_link
                        if currentUrl in already_checked_pages:
                            break
                        else:
                            already_checked_pages.append(currentUrl)
                            print('Redirectin to:' + currentUrl)
                            urls['current_url'] = currentUrl
                            driver.get(currentUrl)
                    else:
                        break

                # 1 We are now in the products listed page
                tmp_state_checker = check_include_stripe()
                if (tmp_state_checker[0] == False and found_psp == False):
                    print('#1 Add to cart checking')
                    content = driver.page_source
                    # Find All button tags with Add to cart text
                    buttons_out = re.findall(r'<button.*?>', content)
                    a_tags_out = re.findall(r'<a(.*?)>', content)

                    pre_checker = add_to_cards(a_tags_out, 'add to cart', 1)
                    if (pre_checker == False):
                        pre_checker = add_to_cards(
                            a_tags_out, 'add to basket', 1)

                    # if we can't find add to cart button there shhould be another steps to reach to that page
                    if (pre_checker == False):
                        # 1 Select options
                        tmp_state_checker = check_include_stripe()
                        if (tmp_state_checker[0] == False):
                            print('#2 Select option checkiing')
                            content = driver.page_source

                            try:
                                buttons_with_select = re.findall(r'<button.*?>', content)
                                a_with_select = re.findall(r'<a(.*?)>', content)


                                link_tag_found = False
                                link_tag_found = links_check(
                                    a_with_select, 'select', 2)
                                if (link_tag_found == False):
                                    buttons_check(
                                        buttons_with_select, 'select', 2)
                            except InvalidArgumentException:
                                link_tag_found = False
                        else:
                            found_psp = True
                            current_state = tmp_state_checker[1]

                        # 2 Select product
                        tmp_state_checker = check_include_stripe()
                        if (tmp_state_checker[0] == False):
                            print('#3 Product selection option checkiing')
                            content = driver.page_source
                            a_with_select = re.findall(r'<a(.*?)>', content)

                            link_tag_found = False
                            link_tag_found = links_check_by_href(
                                a_with_select, 'product/', 3)
                            if (link_tag_found == False):
                                link_tag_found = links_check_by_href(
                                    a_with_select, 'products', 3)
                        else:
                            found_psp = True
                            current_state = tmp_state_checker[1]

                    # Suppose content changed because of select OPTION and PRODUCT get all data again 
                    if (pre_checker == False):
                        content = driver.page_source
                        buttons_out = re.findall(r'<button.*?>', content)
                        a_tags_out = re.findall(r'<a(.*?)>', content)

                    # Searching "add to cart"
                    link_tag_found = links_check(a_tags_out, 'add to cart', 1)
                    if (link_tag_found == False):
                        link_tag_found = links_check_by_href(
                            a_tags_out, 'add to basket', 1)
                    if (link_tag_found == False):
                        link_tag_found = links_check_by_href(
                            a_tags_out, 'buy it now', 1)
                    if (link_tag_found):
                        add_to_cart_found = True
                    
                    tmp_state_checker = check_include_stripe()
                    if (add_to_cart_found and tmp_state_checker[0] == False):
                        content = driver.page_source
                        a_tags = re.findall(r'<a(.*?)>', content)

                        # Check and go to checkout page 
                        checkout_page_found = check_view_cart_and_checkout(a_tags)
                        if(checkout_page_found): 
                            tmp_state_checker = check_include_stripe()
                            if(tmp_state_checker[0]== True):
                                found_psp = True
                                current_state = tmp_state_checker[1]
                            else:
                                # Check proceed checkout page and go to proceed payment page 
                                proceed_page_found = check_proceed_checkout_page()
                                if(proceed_page_found): 
                                    tmp_state_checker = check_include_stripe()
                                    if(tmp_state_checker[0]== True):
                                        found_psp = True
                                        current_state = tmp_state_checker[1]
                                    else: print("#432 Checked until proceed page")
                        
                    elif(tmp_state_checker[0] == True):
                        found_psp == True
                        current_state = tmp_state_checker[1]
                    
                    # If we can't find a tag with "add to cart" time to search with button tag
                    if (found_psp == False and add_to_cart_found == False):
                        button_tag_found = False
                        button_tag_found = buttons_check(
                            buttons_out, 'add to cart', 1)
                        if (button_tag_found == False):
                            button_tag_found = buttons_check(
                                buttons_out, 'add to basket', 1)
                        if (button_tag_found):
                            add_to_cart_found = True

                        content = driver.page_source
                        a_tags = re.findall(r'<a(.*?)>', content)

                        # Check and go to checkout page 
                        checkout_page_found = check_view_cart_and_checkout(a_tags)
                        if(checkout_page_found): 
                            tmp_state_checker = check_include_stripe()
                            if(tmp_state_checker[0]== True):
                                found_psp = True
                                current_state = tmp_state_checker[1]
                            else:
                                # Check proceed checkout page and go to proceed payment page 
                                proceed_page_found = check_proceed_checkout_page()
                                if(proceed_page_found): 
                                    tmp_state_checker = check_include_stripe()
                                    if(tmp_state_checker[0]== True):
                                        found_psp = True
                                        current_state = tmp_state_checker[1]
                                    else: print("#468 Checked until proceed page")

                    # Custom case #1 
                    if (found_psp == False and add_to_cart_found == False):
                        print('Custom case loading')
                        content = driver.page_source
                        a_with_select = re.findall(r'<a(.*?)>', content)

                        link_tag_found = links_check(
                            a_with_select, 'buy now', 1)

                        if (link_tag_found):
                            found_custom_case = checked_custom_case_1()
                            if(found_custom_case): 
                                tmp_state_checker = check_include_stripe()
                                if(tmp_state_checker[0]== True):
                                    found_psp = True
                                    current_state = tmp_state_checker[1]
                                else: 
                                    content = driver.page_source
                                    button_with_select = re.findall(r'<button.*?>', content)
                                    found = buttons_check(button_with_select, 'buy now', 2)
                                    if (found):
                                        content = driver.page_source
                                        a_with_select = re.findall(r'<a(.*?)>', content)

                                        # Check and go to checkout page 
                                        checkout_page_found = check_view_cart_and_checkout(a_with_select)
                                        if(checkout_page_found): 
                                            tmp_state_checker = check_include_stripe()
                                            if(tmp_state_checker[0]== True):
                                                found_psp = True
                                                current_state = tmp_state_checker[1]
                                            else:
                                                # Check proceed checkout page and go to proceed payment page 
                                                proceed_page_found = check_proceed_checkout_page()
                                                if(proceed_page_found): 
                                                    tmp_state_checker = check_include_stripe()
                                                    if(tmp_state_checker[0]== True):
                                                        found_psp = True
                                                        current_state = tmp_state_checker[1]
                                                    else: print("#513 Checked until proceed page")

                else:
                    found_psp = True
                    current_state = tmp_state_checker[1]

                # Check cart page directly
                cart_link_attempt_1 = ""
                if (found_psp == False):
                    suppose_cart_link = original_url + '/cart'
                    cart_link_attempt_1 = suppose_cart_link
                    print('#364 Redirecting to' + suppose_cart_link)
                    driver.get(suppose_cart_link)
                    tmp_state_checker = check_include_stripe()
                    if (tmp_state_checker[0] == True):
                        found_psp = True
                        current_state = tmp_state_checker[1]
                    if (found_psp == False):
                        content = driver.page_source
                        a_tags = re.findall(r'<a(.*?)>', content)
                        
                        # Check and go to checkout page 
                        checkout_page_found = check_view_cart_and_checkout(a_tags)
                        if(checkout_page_found): 
                            tmp_state_checker = check_include_stripe()
                            if(tmp_state_checker[0]== True):
                                found_psp = True
                                current_state = tmp_state_checker[1]
                            else:
                                # Check proceed checkout page and go to proceed payment page 
                                proceed_page_found = check_proceed_checkout_page()
                                if(proceed_page_found): 
                                    tmp_state_checker = check_include_stripe()
                                    if(tmp_state_checker[0]== True):
                                        found_psp = True
                                        current_state = tmp_state_checker[1]
                                    else: print("#432 Checked until proceed page")

                # Check cart link find from resource
                cart_link = ""
                if (found_psp == False):
                    print('Nothing found cart checking')
                    for a in a_tags_home:
                        text = clean_text(a.text)
                        try:
                            cart_link = clean_text(a['href'])
                        except KeyError:
                            cart_link = ""
                        if ('cart' in text and len(cart_link) > 0 and cart_link != cart_link_attempt_1):
                            case_cart_access = True
                            break
                        elif ('/cart' in cart_link and len(cart_link) > 0 and cart_link != cart_link_attempt_1):
                            case_cart_access = True
                            break

                if (case_cart_access):
                    currentUrl = build_link_form_href(cart_link, original_url)
                    urls['current_url'] = currentUrl
                    print("Redirectin to cart: " + currentUrl)
                    driver.get(currentUrl)
                    tmp_state_checker = check_include_stripe()
                    if (tmp_state_checker[0] == True):
                        found_psp = True
                        current_state = tmp_state_checker[1]
                    if (found_psp == False):
                        content = driver.page_source
                        a_tags = re.findall(r'<a(.*?)>', content)
                        
                        # Check and go to checkout page 
                        checkout_page_found = check_view_cart_and_checkout(a_tags)
                        if(checkout_page_found): 
                            tmp_state_checker = check_include_stripe()
                            if(tmp_state_checker[0]== True):
                                found_psp = True
                                current_state = tmp_state_checker[1]
                            else:
                                # Check proceed checkout page and go to proceed payment page 
                                proceed_page_found = check_proceed_checkout_page()
                                if(proceed_page_found): 
                                    tmp_state_checker = check_include_stripe()
                                    if(tmp_state_checker[0]== True):
                                        found_psp = True
                                        current_state = tmp_state_checker[1]
                                    else: print("#584 Checked until proceed page")
                if (found_psp == False and add_to_cart_found):
                    current_state = 'No Stripe or Tap found'
                if (found_psp == False and add_to_cart_found == False):
                    current_state = 'Please manually check'
            else: 
                current_state = tmp_state_checker[1]
        elif (type_of_website == 2):
            current_state = 'Currently can not detect booking sites.'
        elif (type_of_website == 4):
            current_state = 'Currently can not detect travel sites.'
    return current_state
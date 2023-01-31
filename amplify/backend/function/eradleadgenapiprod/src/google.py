from chrome_headless import driver

def clear(link):
    return link.replace("www.", "")


def close_driver():
    driver.quit()


def find_ad(link):
    res = False
    original_url = 'https://'+link
    try:
        driver.get(original_url)
        content = driver.page_source
        scripts = content.split("<script")
        cases = ['google ads', 'googleads', 'googletag', 'googletagmanager']
        for script in scripts:
            if (res):
                break
            for case in cases:
                if (case in script):
                    res = True
                    break
        if (res == False):
            links = content.split("<link")
            for link in links:
                if (res):
                    break
                for case in cases:
                    if (case in link):
                        res = True
                        break
    except:
        print('Google ad link error')

    if (res):
        return 'ad'
    return 'no ad'
from chrome_headless import driver
import requests
import json
import re

access_token = 'EAAQpOuvyMvoBAKyWpPld7RhsWXivitcI753v3JqdEs4xkOYkF58FZAS0aQeK2g2FtZCrSLYHsrLdHaK91ldx71ZBciH6r1TDZB6eJ3kzfzefUsdlpKKs4APqeiafQPpUsYVPSBOEvCxY20ZCJx9smvcSf9JcNLqs9VCwXwK5ytfuZB24i6kvZBdeSFatiK6An5FLSLy8r9Q499F8wNqLoOuXTEz4tJocggZD'


def close_driver():
    driver.quit()

def get_access_token():
    url =  'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=1171232950203130&client_secret=a5de8f3c8aaaa865a38f397ee849ca81&fb_exchange_token='+ access_token
    data1 = requests.get(url)
    response = json.loads(data1.text)
    return response['access_token']
def clean_text(text):
    if (type(text) is str):
        return text.strip().lower()
    return text


def get_user_name(link):
    list = link.split("/")
    index = len(list)-1
    if (list[index] == ''):
        return list[index-1]
    else:
        # Double checking here
        idx = 0
        for el in list: 
            if(el == 'www.instagram.com'):
                index = idx + 1
                break
            idx = idx + 1
        return list[index]


def find_insights(link):
    continue_search = True
    insta = ""
    original_url = 'https://'+link
    try:
        driver.get(original_url)
        content_home_page = driver.page_source
        # Use regular expression to find Instagram links in the HTML
        insta_links = re.findall(r'(https?://(www\.)?instagram\.com/\S+)', content_home_page)
        if insta_links:
            insta = insta_links[0]
        else:
            # Use regular expression to find Instagram links in the text of anchor tags
            insta_links = re.findall(r'<a.*?>(.*instagram.*?)</a>', content_home_page, re.IGNORECASE)
            if insta_links:
                insta = insta_links[0]
    except:
        continue_search = False
    data = {
        'stories': "",
        'followers': "",
        'eng': ""
    }
    if (continue_search):
        name = get_user_name(insta)
        if(len(name) > 0):
            try: 
                # 1 find insta post
                token = get_access_token()
                api1 = 'https://graph.facebook.com/v15.0/17841457679029072?fields=business_discovery.username(' + \
                    name + '){followers_count,media_count}&access_token=' + \
                    token
                data1 = requests.get(api1)
                response = json.loads(data1.text)
                data['followers'] = response['business_discovery']['followers_count']
                data['stories'] = response['business_discovery']['media_count']
                insta_app_id = response['id']
                # 2 story engagement
                api2 = 'https://graph.facebook.com/v15.0/' + insta_app_id + \
                    '/insights?metric=reach&period=week&access_token=' + token
                data2 = requests.get(api2)
                response_reach = json.loads(data2.text)
                collect = 0
                for values in response_reach['data'][0]['values']:
                    collect = collect + values['value']
                data['eng'] = collect
            except: print('error when checking ig')
        else: print('No insta found')
    print(data)
    return data

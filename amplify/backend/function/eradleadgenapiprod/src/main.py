import csv
import similarweb
import psp_v2
import google
import insta
from datetime import datetime
from dateutil.relativedelta import relativedelta

links = []
names = []
psps = []
traffic_1 = []
traffic_2 = []
traffic_3 = []
employees = []
i_posts = []
i_followers = []
i_engagements = []
posts_linkedin = []
google_ads = []

def set_linkedin_data(data):
    employees.append(data.employee)
    posts_linkedin.append(data.post)

def set_trafic_data(data):
    if "values" in data:
        if(len(data['values'])>2):
            traffic_1.append(data['values'][0])
            traffic_2.append(data['values'][1])
            traffic_3.append(data['values'][2])
        else: 
            traffic_1.append("-")
            traffic_2.append("-")
            traffic_3.append("-")
    if "employees" in data:
        employees.append(data['employees'])
def set_insta_data(data):
    if "stories" in data:
        i_posts.append(data['stories'])
        i_followers.append(data['followers'])
        i_engagements.append(data['eng'])
    else: 
        i_posts.append('-')
        i_followers.append('-')
        i_engagements.append('-')

def generate_excel():
    now = datetime.now()

    last_month = now - timedelta(days=30)
    pre_last_month = now - timedelta(days=60)
    pre_pre_last_month = now - timedelta(days=90)

    # Get the name of the last month
    last_month_name = last_month.strftime("%b")
    pre_last_month_name = pre_last_month.strftime("%b")
    pre_pre_last_month_name = pre_pre_last_month.strftime("%b")

    data = [
        ['Merchant Url', 'Merchant name', 'PSP', 
         'Traffic '+ last_month_name, 'Traffic '+ pre_last_month_name, 'Traffic '+ pre_pre_last_month_name,
         'Employee', 'Insta post', 'Insta follower', 'Insta Engagement', 'Google Ads'],
    ]

    for i in range(len(links)):
        data.append([links[i], names[i], psps[i], traffic_1[i], traffic_2[i], traffic_3[i], employees[i], 
                    i_posts[i], i_followers[i], i_engagements[i], google_ads[i]])
    csv_name = './static/files/results.csv'
    csv_name_to_return = '/static/files/results.csv'
    with open(csv_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_name_to_return
def generate_info(links_from_csv):
    index = 0
    filepath = ""
    try:
        for dt in links_from_csv.iterrows():
            if(index == 100): 
                break
            index = index + 1
            link = psp_v2.clean_text(dt[1]['domain'])
            name = psp_v2.clean_text(dt[1]['merchant_name'])
            print("----------------------------------")
            print(link)
            if (len(name) > 0):
                names.append(name)
            else:
                names.append('-')

            if (len(link) > 0):
                links.append(link)
                status = psp_v2.find_psp(link)
                psps.append(status)
                set_trafic_data(similarweb.find_traffic(link))
                google_ads.append(google.find_ad(link))
                set_insta_data(insta.find_insights(link))
                # set_linkedin_data(linkedin.get_data(name))
            else:
                links.append('-')
                psps.append('-')
                set_trafic_data({})
                google_ads.append('-')
                set_insta_data({})

        psp_v2.close_driver()
        google.close_driver()
        insta.close_driver()
        filepath = generate_excel()
    except Exception as e:
        print(e)
        filepath = generate_excel()
    return filepath
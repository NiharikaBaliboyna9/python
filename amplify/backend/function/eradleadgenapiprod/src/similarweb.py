from chrome_headless import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import psp_v2
from selenium.webdriver.chrome.options import Options



def clear(link): 
    return link.replace("www.","")

def find_traffic(link):
    # options=options BUG FIX it doesnot generate once its in the background
    delay = 15 # seconds
    checker_site_url = 'https://www.similarweb.com/website/' + clear(link)
    driver.get(checker_site_url)
    data = {
        "values": [],
        "employees": "-"
    }
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'wa-traffic__chart-data-label')))
        print ("Page is ready!")
        traffic_values = driver.find_elements(By.CLASS_NAME, 'wa-traffic__chart-data-label')
        company_info = driver.find_elements(By.CLASS_NAME, 'data-company-info__row')
        
        for info in company_info:
            text = psp_v2.clean_text(info.text)

            if('employees' in text):
                data['employees'] = text.replace("employees", "")
                break
            
        for value in traffic_values:
            data['values'].append(value.text)
            
        driver.quit()
        return data
    except TimeoutException:
        print ("Loading took too much time! Double checking")
        try: 
            traffic_values = driver.find_elements(By.CLASS_NAME, 'engagement-list__item-value')
            company_info = driver.find_elements(By.CLASS_NAME, 'data-company-info__row')

            for info in company_info:
                text = psp_v2.clean_text(info.text)

                if('employees' in text):
                    data['employees'] = text.replace("employees", "")
                    break
            data['values'].extend(['-', '-'])
            for value in traffic_values:
                if(len(data['values'])<3):  
                    data['values'].append(value.text)
                    break
        except Exception as e:
            print(e)
            print ("Nothing found")

        driver.quit()
        return data
    except Exception as e:
        print(e)
        return data
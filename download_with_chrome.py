import re
import requests
import time
from selenium import webdriver

pdf_base_path = 'pdfs/{}_FU.zip'
download_base_url = 'https://publicaccess.leeds.gov.uk/online-applications/download/?file={}&caseNumber={}'
download_headers = {
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            # 'Referer': 'https://publicaccess.leeds.gov.uk/online-applications/applicationDetails.do?activeTab=documents&keyVal=Q2SU95JBG6G00',
            'Host': 'publicaccess.leeds.gov.uk',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Cookie': 'JSESSIONID=6EiaCHzx2SOwOWFZ6XUX1QIwT7Eld4NvwuUzv9iV.pdaidxwam02',
        }

def parse_page_info(page_text):
    """
        解析page页面获取下载链接
    """
    try:
        file_url = re.search(r'value="(.*?/APPLICATION_FORM_-_WITHOUT_PERSONAL_DATA-.*?.pdf)"', page_text).group(1)
        print(file_url)
        caseNumber = re.search(r'<input type="hidden" name="caseNumber" value="(.*?)">', page_text).group(1)
    except Exception as e:
        print('Error,', e)
    else:
        download_url = download_base_url.format(file_url, caseNumber)
        return download_url

    return False

def download(browser, url):
    browser.get(url)
    page_source = browser.page_source
    with open('page_source.txt', 'w', encoding='utf-8') as f:
        f.write(page_source)
    download_url = parse_page_info(page_source)
    if not download_url: print('该页面不存在目标文件', url)
    else:
        browser.get(download_url)


def init_webdriver(chrome_download_path):
    
    
    option = webdriver.ChromeOptions()

    prefs = {
        'profile.default_content_settings.popups': 0,
        "safebrowsing.enabled": True,
        'download.default_directory': chrome_download_path,
        }
    option.add_experimental_option('prefs', prefs)
    

    head_browser_with_option = webdriver.Chrome('chromedriver/chromedriver.exe', chrome_options=option)
    head_browser = webdriver.Chrome('chromedriver/chromedriver.exe')
    return head_browser

def main(path):
    # chrome_download_path = base_download_path+re.search(r'(data/.*?/[\d]{4}/).*?.txt', path).group(1)
    chrome_download_path = ''
    
    browser = init_webdriver(chrome_download_path)
    with open(path, 'r') as f:
        urls = f.readlines()
    for url in urls:
        try:
            print(url)
            download(browser, url)
        except Exception as e:
            print(e)
            pass


download_file_path = (
    'data/seccess/2015/2015_seccess_info_page.txt',
    'data/seccess/2016/2016_seccess_info_page.txt',
    'data/seccess/2017/2017_seccess_info_page.txt',
    'data/seccess/2018/2018_seccess_info_page.txt',
    'data/seccess/2019/2019_seccess_info_page.txt',
    'data/seccess/2020/2020_seccess_info_page.txt',

    'data/fail/2015/2015_fail_info_page.txt',
    'data/fail/2016/2016_fail_info_page.txt',
    'data/fail/2017/2017_fail_info_page.txt',
    'data/fail/2018/2018_fail_info_page.txt',
    'data/fail/2019/2019_fail_info_page.txt',
    'data/fail/2020/2020_fail_info_page.txt',
)

if __name__ == "__main__":
    base_download_path = 'F:/job/compamy_job/jiedan'
    path = 'data/fail/all_data.txt'
    main(path)
    """
    for path in download_file_path:
        main(path)
    """
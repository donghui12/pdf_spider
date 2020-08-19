import requests
import re
import time
import copy
import pickle

class UKSpider(object):
    def __init__(self):
        self.HOST = 'https://publicaccess.leeds.gov.uk'
        self.search_base_url = 'https://publicaccess.leeds.gov.uk/online-applications/advancedSearchResults.do?action=firstPage'
        self.search_base_index_url = 'https://publicaccess.leeds.gov.uk/online-applications/pagedSearchResults.do?action=page&searchCriteria.page={}'
        self.download_base_url = 'https://publicaccess.leeds.gov.uk/online-applications/download/?file={}&caseNumber={}'
        self.info_page_base_url = 'https://publicaccess.leeds.gov.uk/online-applications/applicationDetails.do?activeTab=documents&keyVal={}'
        self.pdf_base_path = 'pdfs/{}_FU.zip'

        self.load_session()  # 加载session
        self.chunk_size = 128

    def connect(self, url, headers, parameters):
        """
            连接url, 主要是用于请求info_page
        """
        try:
            resp = requests.get(url, headers=headers, params=parameters)
            if resp.status_code == 200:
                return resp.text
            else:
                print('{}, 连接失败:{}'.format(url, resp.status_code))
                return None
        except Exception as e:
            print(e, url)
            return None
    
    @property
    def PARAMETERS(self):
        """
            参数
        """
        base_parameters = {}
        return base_parameters

    def HEADERS(self, referer):
        """
            初始化HEADERS
        """
        base_header = {
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'publicaccess.leeds.gov.uk',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Cookie': 'JSESSIONID=OR9H9l7j2197HuNCfQkjY-cnLPeMpj8Yb5CK25aT.pdaidxwam02',
            'Referer': referer, 
        }      

        return base_header
    
    def get_first_info_page_url(self):
        """
            请求首页搜索页面，获取session
        """
        search_data = {
            "searchCriteria.caseType": "FU", 
            "searchCriteria.caseStatus": "Decided", 
            # "searchCriteria.caseDecision": "R", 
            "searchCriteria.caseDecision": "A", 
            "searchCriteria.appealStatus": "", 
            "caseAddressType": "Application", 
            "searchType": "Application", 
            "date(applicationValidatedStart)": "01/09/2009", 
            "date(applicationValidatedEnd)": "01/12/2009", 
        }
        self.load_session()
        try:
            resp = self.session.post(self.search_base_url,data=search_data)
            if resp.status_code != 200:
                print('error status code', resp.status_code)
                return None
        except Exception as e:
            print('Error, ', e)
            return None
        page_number = re.search('<span class="showing"><strong>Showing 1-10</strong> of (.*?)</span>', resp.text).group(1)

        self.save_session()
        return page_number
    
    def save(self, text):
        with open('./text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
    def save_info_url(self, urls):
        with open('info_url.txt', 'a', encoding='utf-8') as f:
            for url in urls:
                full_url = self.info_page_base_url.format(url)
                f.write(full_url+'\n')
                print('获取成功!')
    
    def save_session(self):
        """
            保存session
        """
        with open('session', 'wb') as f:
            pickle.dump(self.session, f)
    
    def load_session(self):
        """
            加载session
        """
        try:
            with open('session', 'rb') as f:
                self.session = pickle.load(f)
        except FileNotFoundError as e:
            print('session不存在，重新生成')
            self.session = requests.session()

    def parse_search_page(self, search_page):
        """
            解析搜索页面，获取具体info_page_url
        """
        try:
            page_number = re.search(r'<strong>([\d]{1,2})</strong>', search_page).group(1)
        except Exception as e:
            print(e)
            page_number = '-1'
    
        info_urls = re.findall(r'keyVal=(.*?)&amp', search_page)
        if not info_urls:
            print('None urls', page_number)
        
        return info_urls
    
    def parse_info_page(self, info_page):
        """
            这是具体页面进行解析，获取下载链接
        """
        try:
            file_url = re.search(r'value="(.*?/APPLICATION_FORM_-_WITHOUT_PERSONAL_DATA-.*?.pdf)"', info_page).group(1)
            caseNumber = re.search(r'<input type="hidden" name="caseNumber" value="(.*?)"/>', info_page).group(1)
        except Exception as e:
            print('Error,', e)
        else:
            download_url = self.download_base_url.format(file_url, caseNumber)
            return download_url

        return None

    def download(self, url, referer):
        """
            下载pdf
        """
        print(url)
        if not url:
            print('None')
            pass
        else:
            HEADERS = self.HEADERS(referer)
            
            re_caseNumber = re.search(r'&caseNumber=(.*?)/FU', url).group(1)
            caseNumber = re.sub('/', '_', re_caseNumber)
            file_name = re.search(r'file=.*?/(.*?).pdf', url).group(1)

            pdf_resp = requests.get(url, stream=True, headers=HEADERS)
            if pdf_resp.status_code != 200:
                print('{}--下载失败'.format(referer))
                with open('failed.txt', 'a') as f:
                    f.write(url+'\n')
            else:
                path = self.pdf_base_path.format(caseNumber)
                with open(path, 'wb') as fd:
                    for chunk in pdf_resp.iter_content(chunk_size=self.chunk_size):
                        fd.write(chunk)
                
                with open('seccess.txt', 'a') as f:
                    f.write(url+'\n')

                print('{}--下载成功'.format(url))

    def get_info_page_url(self):
        """
            获取info_page_url, 并保存下来
        """
        page_number = self.get_first_info_page_url()
        print('总页面', page_number)

        for page_idx in range(1, int(int(page_number)/10)+1):
            search_url = self.search_base_index_url.format(page_idx)
            search_page = self.session.get(search_url, headers=self.HEADERS(search_url))
            
            info_urls = self.parse_search_page(search_page.text)
            print(info_urls)
            self.save_info_url(info_urls)
    
    def get_download_urls(self):
        """
            获取下载urls
        """
        with open('info_page.txt', 'r', encoding='utf-8') as f:
            info_page_urls = f.readlines()
        
        for rd_info_page_url in info_page_urls[::-1]:
            info_page_url = rd_info_page_url.replace('\n', '')
            
            info_page_text = self.session.get(info_page_url)
            if info_page_text is None:
                print(rd_info_page_url)
                time.sleep(2)
            else:
                download_url = self.parse_info_page_2(info_page_text)
                print(download_url)
                if download_url is None:
                    print(rd_info_page_url)
                    time.sleep(2)
                else:
                    self.save_download_url(download_url)
        
    def test_parse_info_page(self):
        with open('./info_page_text.txt', 'r', encoding='utf-8') as f:
            info_page = f.read()
        download_url = self.parse_info_page_2(info_page)
        print('this is download_url:', download_url)

    
    def get_download_urls(self):
        """
            获取下载urls
        """
        with open('info_url.txt', 'r', encoding='utf-8') as f:
            info_page_urls = f.readlines()
        
        for rd_info_page_url in info_page_urls:
            info_page_url = rd_info_page_url.replace('\n', '')
            
            info_page_text = requests.get(info_page_url).text
            if info_page_text is None:
                print(rd_info_page_url)
                time.sleep(2)
            else:
                download_url = self.parse_info_page(info_page_text)
                print(download_url)
                if download_url is None:
                    print(rd_info_page_url)
                    time.sleep(2)
                else:
                    self.download(download_url, info_page_url)
                    """
                    with open('download_urls.txt', 'a') as f:
                        f.write(download_url+'\n')
                    """
    
    def get_pdf(self):
        with open('download_urls.txt', 'r') as f:
            urls = f.readlines()

        for url in urls:
            self.download(url)


if __name__=="__main__":
    base_url = ''

    ukspider = UKSpider()
    ukspider.get_info_page_url()  # 获取具体页面的url
    # ukspider.get_download_urls()  # 获取具体下载连接 pdf的下载连接
    # ukspider.get_pdf()  # 获取pdf文件
    
import PyPDF2
import pdfplumber
import time
import re
import json
import os
import csv

def extract_content(pdf_path):
    """
        文本读取载入
    """
    status = re.search(r'.\\data\\(.*?)\\', pdf_path).group(1)
    # status = re.search(r'.\\example\\(.*?)\\', pdf_path).group(1)
    year = re.search(r'\\([\d]{4})\\', pdf_path).group(1)
    

    
    with pdfplumber.open(pdf_path) as pdf_file:
        # 使用 PyPDF2 打开 PDF 用于提取图片
        pdf_image_reader = PyPDF2.PdfFileReader(open(pdf_path, "rb"))
        print('本pdf总页数为:', pdf_image_reader.getNumPages())

        content = ''
        # len(pdf.pages)为PDF文档页数，一页页解析
        for i in range(len(pdf_file.pages)):
            print("当前第 %s 页" % i)
            # pdf.pages[i] 是读取PDF文档第i+1页
            page_text = pdf_file.pages[i]
            # page.extract_text()函数即读取文本内容
            page_content = page_text.extract_text()

            if page_content:
                content = content + page_content +'\n'
    return year, status, content
    

def save(page):
    with open('page_3.txt', 'w', encoding='utf-8') as f:
        f.write(page)

def parse_2015_page(year, status, content, pdf_path):
    """
        单独处理一个pdf文件
    """
    re_content = re.sub('\n', 'AJDH', content)
    try:
        re_first_part = re.search(r'Site Address Details(.*?)5.  [Pedestrian|Pre]', re_content) or re.search(r'Site Address Details(.*?)5. [Pedestrian|Pre]', re_content)
        first_part = re_first_part.group(1)
    except AttributeError as e:
        print('Error', pdf_path)
        return None
    
    first_part_data = parse_2015_first_part(first_part, re_content)
    
    try:
        Description = re.search(r'Please describe the proposed works:(.*?)Has the work', re_content).group(1)
    except AttributeError as e:
        Description = ''
    data = {}
    materials_part_content = re.search(r'Materials(.*)[\d]{1,2}. [A-Z]', re_content).group(1)
    materials_part = parse_2015_second_part(materials_part_content)

    data['year'] = year
    data['status'] = status
    data['number'] = first_part_data[0]
    data['Suffix'] = first_part_data[1]
    data['Property_name'] = first_part_data[2]
    data['address_line_1'] = first_part_data[3]
    data['address_line_2'] = first_part_data[4]
    data['Town'] = first_part_data[5]
    data['County'] = first_part_data[6]
    data['Postcode'] = first_part_data[7]
    data['Easting_x'] = first_part_data[8]
    data['Northing_y'] = first_part_data[9]
    
    data['Description'] = re.sub('AJDH', '', Description)
    for i in range(1, 16):
        name = 'meterials_{}'.format(str(i))
        if i < len(materials_part):
            data[name] = re.sub('AJDH', '', materials_part[i])
        else:
            data[name] = ''
    
    print(data)
        
    return data

def parse_2019_page(year, status, content, pdf_file):
    """
        单独处理一个pdf文件
    """
    re_content = re.sub('\n', 'AJDH', content)
    try:
        re_first_part = re.search(r'Site Address(.*?)2. Applicant Details', re_content) or re.search(r'Site Address Details(.*?)5. [Pedestrian|Pre]', re_content)
        first_part = re_first_part.group(1)
    except AttributeError as e:
        print('Error', pdf_path)
        return None 
    
    first_part_data = parse_2019_first_part(first_part ,re_content)
    
    try:
        Description = re.search(r'Please describe the proposed works:(.*?)Has the work', re_content).group(1)
    except AttributeError as e:
        Description = ''
    data = {}

    materials_part_content = re.search(r'Materials(.*)[\d]{1,2}. [A-Z]', re_content).group(1)
    materials_part = parse_2015_second_part(materials_part_content)

    data['year'] = year
    data['status'] = status
    data['number'] = first_part_data[0]
    data['Suffix'] = first_part_data[1]
    data['Property_name'] = first_part_data[2]
    data['address_line_1'] = first_part_data[3]
    data['address_line_2'] = first_part_data[4]
    data['address_line_3'] = first_part_data[5]
    data['Town'] = first_part_data[6]
    data['Postcode'] = first_part_data[7]
    data['Easting_x'] = first_part_data[8]
    data['Northing_y'] = first_part_data[9]
    
    data['Description'] = re.sub('AJDH', '', Description)
    for i in range(1, 15):
        name = 'meterials_{}'.format(str(i))
        if i < len(materials_part):
            data[name] = re.sub('AJDH', '', materials_part[i])
        else:
            data[name] = ''
    return data
    

def parse_2015_first_part(part, content):
    try:
        number = re.search(r'House:(.*?)Suffix',part).group(1)
    except AttributeError as e:
        print("number Error")
        number = ''

    try:
        Suffix = re.search(r'Suffix:(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print("Suffix Error", e)
        Suffix = ''
    
    try:
        Property_name = re.search(r'House name:(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print("Property_name Error")
        Property_name = ''
    
    try:
        address_line = re.findall(r'Street address: (.*?)AJDH(.*?)AJDH', part)
        address_line_1 = address_line[0][0]
        address_line_2 = address_line[0][1]
    except AttributeError as e:
        print('address error', e)
        address_line_1 = ''
        address_line_2 = ''
    
    try:
        Town = re.search(r'Town/City: (.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('address error')
        Town = ''
    
    try:
        County = re.search(r'County:(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('County error')
        County = ''
    
    try:
        Postcode = re.search(r'Postcode: (.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('Postcode error')
        Postcode = ''

    try:
        Easting_x = re.search(r'Easting: (.*?)AJDH', part).group(1)
        Northing_y = re.search(r'Northing: (.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('x, y Error')
        Easting_x = ''
        Northing_y = ''

    first_part = (number, Suffix, Property_name, address_line_1, address_line_2, Town, County, Postcode, Easting_x, Northing_y)
    return first_part

def parse_2015_second_part(part):
    """
        处理第二部分
    """
    try:
        Materials_1 = re.findall(r'finishes:(.*?)Description',part)
    except AttributeError as e:
        print("Materials_1 Error")
        Materials_1 = ''
    
    try:
        Materials_2 = re.findall(r'finishes:(.*?)Roof',part)
    except AttributeError as e:
        print("Materials_2 Error")
        Materials_2 = ''
    
    try:
        Materials_3 = re.findall(r'statement:(.*)AJDH',part)
    except AttributeError as e:
        print("Materials_3 Error")
        Materials_3 = ''
    
    Materials = []

    for i in Materials_1:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)
    for i in Materials_2:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)
    for i in Materials_3:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)

    return Materials

def parse_2019_first_part(part, content):
    try:
        number = re.search(r'Number(.*?)AJDH',part).group(1)
    except AttributeError as e:
        print("number Error")
        number = ''

    try:
        Suffix = re.search(r'Suffix(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print("Suffix Error", e)
        Suffix = ''
    
    try:
        Property_name = re.search(r'Property name(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print("Property_name Error")
        Property_name = ''
    
    try:
        address_line_1 = re.search(r'Address line 1(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('address1 error', e)
        address_line_1 = ''
        
    try:
        address_line_2 = re.search(r'Address line 1(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('address2 error', e)
        address_line_2 = ''
        
    try:
        address_line_3 = re.search(r'Address line 3(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('address3 error', e)
        address_line_3 = ''
    
    try:
        Town = re.search(r'Town/city(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('Town error')
        Town = ''
    
    try:
        Postcode = re.search(r'Postcode(.*?)AJDH', part).group(1)
    except AttributeError as e:
        print('Postcode error')
        Postcode = ''
    save(part)
    try:
        Easting_x = re.findall(r'([\d]{6})AJDH', part)[0]
        Northing_y = re.findall(r'([\d]{6})AJDH', part)[1]
    except AttributeError as e:
        print('x, y Error', e)
        Easting_x = ''
        Northing_y = ''

    first_part = (number, Suffix, Property_name, address_line_1, address_line_2, address_line_3, Town, Postcode, Easting_x, Northing_y)
    return first_part


def parse_2019_second_part(part):
    """
        处理第二部分
    """
    try:
        Materials_1 = re.findall(r'(optional): (.*?)AJDH',part)
    except AttributeError as e:
        print("Materials_1 Error")
        Materials_1 = ''
    
    try:
        Materials_2 = re.findall(r'finishes: (.*?)AJDH',part)
    except AttributeError as e:
        print("Materials_2 Error")
        Materials_2 = ''
    
    try:
        Materials_3 = re.findall(r'statement: (.*)AJDH',part)
    except AttributeError as e:
        print("Materials_3 Error")
        Materials_3 = ''
    
    Materials = []

    for i in Materials_1:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)
    for i in Materials_2:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)
    for i in Materials_3:
        Material = re.sub('AJDH', '', i)
        Materials.append(Material)

    return Materials

def to_csv(datas, headers, csv_file):
    """
        保存到csv文件
    """
    with open(csv_file, 'a', newline='') as f:
    # 标头在这里传入，作为第一行数据
        writer = csv.DictWriter(f, headers)
        # writer.writeheader()
        writer.writerow(datas)

def save_info(data):
    with open('infos.json', 'a') as f:
        json.dump(data, f)
        f.write('\n')

def walk_dir(floder):
    files = []
    for parent, dirnames, filenames in os.walk(floder):
        for file in filenames:
            filepath = os.path.join(parent, file)
            if os.path.isdir(file):
                walk_dir(filepath)
            elif filepath.endswith('.pdf'):
                # print(filepath)
                files.append(filepath)
    return files

def main():
    floder = r'.\data\seccess\2020'
    # test_floder = r'.\example'
    files = walk_dir(floder)
    _2015_headers = ['year', 'status', 'number', 'Suffix', 'Property_name', 'address_line_1', 'address_line_2', 'Town', 
    'County', 'Postcode', 'Easting_x', 'Northing_y', 'Description', 'meterials_1',	'meterials_2',	'meterials_3',
    'meterials_4',	'meterials_5',	'meterials_6',	'meterials_7',	'meterials_8',	'meterials_9',	'meterials_10',
    	'meterials_11',	'meterials_12',	'meterials_13',	'meterials_14',	'meterials_15']
    _2019_headers = ['year', 'status', 'number', 'Suffix', 'Property_name', 'address_line_1', 'address_line_2', 
    'address_line_3', 'Town', 'Postcode', 'Easting_x', 'Northing_y', 'Description', 'meterials_1',	'meterials_2',	'meterials_3',
    'meterials_4',	'meterials_5',	'meterials_6',	'meterials_7',	'meterials_8',	'meterials_9',	'meterials_10',
    	'meterials_11',	'meterials_12',	'meterials_13',	'meterials_14',	'meterials_15']
    
    for pdf_file in files:
        try:
            # pdf_file = r'.\example\fail\2015\APPLICATION_FORM_-_WITHOUT_PERSONAL_DATA-1224474.pdf'
            year, status, content = extract_content(pdf_file)
            # 由于年份不同，对此的处理函数也各不相同
            if int(year) >= 2019:
                data = parse_2019_page(year, status, content, pdf_file)
                to_csv(data, _2019_headers, '2019_result_new.csv')
            else:
                pass
                # data = parse_2015_page(year, status, content, pdf_file)
                # to_csv(data, _2015_headers, '2015_result.csv')
                # save(content)
                # break
        except Exception as e:
            print('Error', e)
            pass
        
main()   
# data = [{'number':'24', 'shuffix': '', 'local_x': ' 45215', 'des':'dhsauojdhsjkahdsjka;hdlskhajdls'}]
# to_csv(data)
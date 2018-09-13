from bs4 import BeautifulSoup
import os, math, re
import pandas as pd
import requests
from lxml.html import fromstring
from itertools import cycle

HOME_DIR = "/Users/zeeshannawaz/UpWork/Scrapping/~01df281dd2f50eee26 - Scrapping foot Items/Data"


def get_response(google_search_url, payload, my_headers, proxies):
    try:
        pool = cycle(proxies)
        proxy = next(pool)
        response = requests.get(google_search_url, params=payload, headers=my_headers,
                                           proxies={"http": proxy, "https": proxy})
        if response.ok != False:
            return response
            get_response(google_search_url, payload, my_headers, proxies)
    except:
        get_response(google_search_url, payload, my_headers, proxies)


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


def get_reading_urls_from_file(file_path):
    return pd.read_excel(file_path)

def get_total_items_for_country(soup):
    selector = 'div > div > h3'
    return int(soup.select(selector)[1].text.split(' ')[0])


def scrap_url(country_name, main_url, count, output_file, wiki_file, not_found_count):
   # proxies = get_proxies()
   # proxy_pool = cycle(proxies)
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    total_items = get_total_items_for_country(soup)
    items_per_page = 10
    total_pages = math.ceil(total_items/items_per_page)

    for index in range(1,total_pages+1):
        # Scrap the urls for ten elements on this page
        if index != 1:
            url_parts = main_url.split('?')
            main_url2 = url_parts[0] + 'page/' + str(index)  + '/?' + url_parts[1]
        else:
            main_url2 = main_url
        response = requests.get(main_url2)
        soup = BeautifulSoup(response.text, 'html.parser')

        selector = 'div > div > div > a'
        products_tags = soup.select(selector)
        for item in products_tags:
            if 'prodotto' in item['href']:

                # Declarations
                production_method = ""
                appearence_and_flavour = ""
                production_area = ""
                production = ""
                surface = ""
                history = ""
                country = ""
                category = ""
                category_name = ""
                product_class = ""

                gastronomy = ""
                marketing = ""
                distinctive_features = ""
                view_product_specification = ""
                download_ebook = ""
                operators = ""
                image_address1 = ""
                image_address2 = ""
                image_address3 = ""
                image_address4 = ""
                turnover = ""
                is_door_database_check = True  # If found later, set it false
                is_found_in_doors = False
                is_found_in_wiki = True

                number = count
                url = item['href']
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                #name = soup.title.text.split("::")[1].strip()
                name = soup.title.text.split("::")[-3:][0].split('(')[0].strip()
                product_url = url




                main_page_text_tags = str(soup.find_all('div','single-content')[0]).split('<h3 style="margin-bottom:0px; padding-bottom:0px">')

                for tags in main_page_text_tags:
                    if 'class="single-content' not in tags:
                        category_name = tags.split('</h3>\n')[0].strip()
                        if category_name == "Production Area":
                            production_area = tags.split('</h3>\n')[1].strip().replace(',','')
                            continue
                        if category_name == 'Appearance and Flavour':
                            appearence_and_flavour = tags.split('</h3>\n')[1].strip().replace(',','')
                            continue
                        if category_name == 'Production Method':
                            production_method = tags.split('</h3>\n')[1].strip().replace(',','')
                            continue
                        if category_name == "History":
                            history = tags.split('</h3>\n')[1].strip().replace(',','')
                            continue
                        if category_name == 'Gastronomy':
                            gastronomy = tags.split('</h3>\n')[1].strip().replace(',','')
                            continue
                        if category_name == "Marketing":
                            marketing = tags.split('</h3>\n')[1].strip().replace(',','')
                            marketing = marketing.replace('\n','').replace('<\br>','').strip()
                            continue
                        if category_name == "Distinctive Features":
                            distinctive_features = tags.split('</h3>\n')[1].strip().replace(',','').replace('</div>','').rstrip(' ')
                            distinctive_features = distinctive_features.replace('\n','').strip()
                            continue

                selector = 'div > div > strong > a'
                links_tags = soup.select(selector)
                for tags in links_tags:
                    if tags.text == "Download E-BOOK page":
                        download_ebook = 'http://www.qualigeo.eu/' + tags['href']
                        continue
                    if tags.text == "View Product Specification":
                        view_product_specification = tags['href']
                        is_door_database_check = False
                        continue

                remaining_links = soup.find_all('div','sidebar-indicatori')
                for tags in remaining_links:
                  #  if 'Registration' in tags.text:
                  #      registration_date = tags.text.replace('\t','').strip().split('\n')[1].replace(' ','').strip(',')
                    if 'Country' in tags.text:
                        country = tags.text.replace('\t','').strip().split()[1].replace(',','')
                    if 'Category' in tags.text:
                        if "SPIRITS" in tags.text:
                            category = tags.text.split('\t')[-1:]
                        else:
                            category = tags.text.replace('\t','').strip().split()[1].replace(',','')
                    if 'Class' in tags.text:
                        product_class = " ".join(tags.text.replace('\t','').strip().split()[1:]).replace(',','')
                    if 'Production' in tags.text:
                        if count == 18:
                            c = 1
                        if len(tags.text.replace('\t','').strip().split()[1].split(')')) < 2:
                            production = ""
                        else:
                            production = tags.text.replace('\t','').strip().split()[1].split(')')[1].strip(',').replace(',','')
                    if 'Turn' in tags.text:
                        turnover = tags.text.replace('\t','').strip().split()[2].strip('€').strip(')').replace(',','')
                    if 'Surface' in tags.text:
                        surface = tags.text.replace('\t','').strip().split()[1].split(')')[1].replace(',','')
                    if 'Operators' in tags.text:
                        operators = tags.text.replace('Operators','').strip(',').strip()

                selector = 'div > div > img'
                image_tags = soup.select(selector)
                for img in image_tags:
                    if 'wp-content' in img.text and '.jpg' in img.text:
                        if len(image_address1) < 3:
                            image_address1 = img['src']
                        elif len(image_address2) < 3:
                            image_address2 = img['src']
                        elif len(image_address3) < 3:
                            image_address3 = img['src']
                        else:
                            image_address4 = img['src']


                # Check Doors database if needed
                if is_door_database_check:
                    print("Not found")




                    if country_name == "France":
                        filter_country = "FR"
                    if country_name == "Spain":
                        filter_country = "ES"
                    if country_name == "Greece":
                        filter_country = "EL"
                    if country_name == "Hungary":
                        filter_country = "HU"
                    if country_name == "germany":
                        filter_country = "DE"
                    if country_name == "portugal":
                        filter_country = "PT"
                    if country_name == "austria":
                        filter_country = "AT"
                    if country_name == "belgium":
                        filter_country = "BE"
                    if country_name == "luxembourg":
                        filter_country = "LU"
                    if country_name == "croatia":
                        filter_country = "HR"

                    if len(name.split(" ")) > 1:
                        search_name  = name
                        search_name = " ".join(search_name.split(' ')[:-1]).strip()
                    else:
                        search_name = name
                    doors_url = 'http://ec.europa.eu/agriculture/quality/door/list.html?country='+ country +'&recordStart=0&filter.dossierNumber=&filter.comboName=' + str(search_name.replace(' ','%20')) +'&filterMin.milestone__mask=&filterMin.milestone=&filterMax.milestone__mask=&filterMax.milestone=&filter.country='+ filter_country + '&filter.category=&filter.type=&filter.status='
                    response = requests.get(doors_url)
                    soup = BeautifulSoup(response.text,'html.parser')

                    doors_name = ""
                    countries_of_origin = ""
                    dossier_number = ""
                    status = ""
                    application_type = ""
                    type_of_product = ""
                    date_of_submission = ""
                    date_of_publication = ""
                    date_of_registration = ""
                    producer_group_name = ""
                    producer_group_address = ""

                    volume = ""
                    proof = ""
                    color = ""
                    ingrediants = ""

                    if not 'href' in str(soup.find_all('td')[38]): # Case when product not found in Doors website
                        # Now check on wiki
                        is_found_in_doors = False
                        not_found_count += 1
               #         is_found_in_doors = False
               #         my_headers = {'User-agent': 'Mozilla/11.0'}
               #         google_search_url = 'http://www.google.com/search'
               #         payload = {'q': "https://wikipedia.org " + name, 'start': str(0), 'num': str(10)}

#                        proxy = next(proxy_pool)

 #                       response = get_response(google_search_url, payload, my_headers, proxies)

             #           response = requests.get(google_search_url, params=payload, headers=my_headers,
             #                                   proxies={"http": proxy, "https": proxy})
  #                      soup = BeautifulSoup(response.text, 'html.parser')
   #                     if count == 30:
   #                         co = 6
   #                     wiki_page_url = soup.find_all('h3', class_='r')[0].find('a')['href']\
   #                         .split("&")[0].strip('/url?q=')
   #                     response = requests.get(wiki_page_url)
   #                     soup = BeautifulSoup(response.text, 'html.parser')
   #                     tr_tags = soup.find_all('tr')
    #                    if not len(tr_tags) > 0:
    #                         is_found_in_wiki = False
    #                     for tr_tag in tr_tags:
    #                         if len(tr_tag.find_all('th')) > 0:
    #                             if tr_tag.find_all('th')[0].text == "Type":
    #                                 type_of_product = tr_tag.find_all('td')[0].text
    #                             if tr_tag.find_all('th')[0].text == "Country of origin":
    #                                 countries_of_origin = tr_tag.find_all('td')[0].text
    #                             if "volume" in tr_tag.find_all('th')[0].text:
    #                                 volume = tr_tag.find_all('td')[0].text.strip('\n').strip('Äì')
    #                             if "Proof" in tr_tag.find_all('th')[0].text:
    #                                 proof = tr_tag.find_all('td')[0].text.strip('\n').strip().strip('Äì')
    #                             if "Colour" in tr_tag.find_all('th')[0].text:
    #                                 color = tr_tag.find_all('td')[0].text.strip('\n').strip().strip('Äì')
    #                             if "Ingredients" in tr_tag.find_all('th')[0].text:
    #                                 ingrediants = tr_tag.find_all('td')[0].text.replace('\n',' ').strip().replace(',',' ')
    #







                    else:
                        product_doors_url = soup.find_all('td')[38].find_all('a')[0]['href']
                        # for xx in xxx:
                        #     if len(xx.find_all('a')) > 0 and 'href' in xx.find_all('a'):
                        #         if 'chkDenomination' in xx.find_all('a')[0]['href']:
                        #             product_doors_url = xx.find_all('a')[0]['href']

                        response = requests.get(product_doors_url)
                        soup = BeautifulSoup(response.text,'html.parser')



                        for index in range(0,len(soup.find_all('td','title'))):
                            if 'Name' in str(soup.find_all('td','title')[index].text):
                                doors_name = soup.find_all('td','title')[index+1].text.strip()
                                continue
                            if 'Countries of Origin' in str(soup.find_all('td','title')[index].text):
                                countries_of_origin = soup.find_all('td','title')[index+1].text.strip()
                                continue
                            if 'Application Type' in str(soup.find_all('td', 'title')[index].text):
                                application_type = soup.find_all('td', 'title')[index + 1].text.strip()
                                continue
                            if 'Dossier Number' in str(soup.find_all('td', 'title')[index].text):
                                dossier_number = soup.find_all('td', 'title')[index + 1].text.strip()
                                continue
                            if 'Type of Product' in str(soup.find_all('td', 'title')[index].text):
                                countries_of_origin = soup.find_all('td', 'title')[index + 1].text.strip()
                                continue
                            if 'Status' in str(soup.find_all('td', 'title')[index].text):
                                status = soup.find_all('td', 'title')[index + 1].text.strip()
                                continue
                            if 'Date of Registration' in str(soup.find_all('td', 'title')[index].text):
                                dd = soup.find_all('td', 'title')[index].text.replace('\n','').replace('\t','').replace('\r','')
                                date_of_registration = re.search(r'Date of Registration: \xa0\xa0\xa0\xa0\xa0..........', str(dd))[0]
                                date_of_registration = date_of_registration.replace('\xa0','').split(':')[1].strip()
                            if 'Date of Publication' in str(soup.find_all('td', 'title')[index].text):
                                dd = soup.find_all('td', 'title')[index].text.replace('\n', '').replace('\t','').replace('\r', '')
                                date_of_publication = re.search(r'Date of Publication: \xa0\xa0\xa0\xa0\xa0..........', str(dd))[0]
                                date_of_publication = date_of_publication.replace('\xa0', '').split(':')[1].strip()
                            if 'Date of Submission' in str(soup.find_all('td', 'title')[index].text):
                                dd = soup.find_all('td', 'title')[index].text.replace('\n', '').replace('\t','').replace('\r', '')
                                date_of_submission = re.search(r'Date of Submission: \xa0\xa0\xa0\xa0\xa0..........', str(dd))[0]
                                date_of_submission = date_of_submission.replace('\xa0', '').split(':')[1].strip()











      #          if not is_found_in_doors and is_found_in_wiki:
      #              output_file = wiki_file



                output_file.writelines("Name:," + name + '\n')
                output_file.writelines("URL:," + url+ '\n')
                if len(production_method) > 5:
                    output_file.writelines("Production Method:," + production_method+ '\n')
                if len(appearence_and_flavour) > 5:
                    output_file.writelines("Appearance and Flavour:," + appearence_and_flavour+ '\n')
                if len(production_area) > 5:
                    output_file.writelines("Production Area:,"+ production_area+ '\n')
                if len(history) > 5:
                    output_file.writelines("History:," + history+ '\n')
                if len(gastronomy) > 5:
                    output_file.writelines("Gastronomy:," + gastronomy+ '\n')
                if len(marketing) > 5:
                    output_file.writelines("Marketing:," + marketing+ '\n')
                if len(distinctive_features) > 5:
                    output_file.writelines("Distinctive Features:," + distinctive_features+ '\n')
                if len(image_address1) > 5:
                    output_file.writelines("Address Image 1:," + image_address1+ '\n')
                if len(image_address2) > 5:
                    output_file.writelines("Address Image 2:," + image_address2+ '\n')
                if len(image_address3) > 5:
                    output_file.writelines("Address Image 3:," + image_address3+ '\n')
                if len(image_address4) > 5:
                    output_file.writelines("Address Image 4:," + image_address4+ '\n')
                if len(download_ebook) > 5:
                    output_file.writelines("Download E-Book Page:," + download_ebook+ '\n')
                if view_product_specification != "":
                    output_file.writelines("View Product Specification:," + view_product_specification + '\n')
                if len(country) > 4:
                    output_file.writelines("Country:," + country+ '\n')
                if len(category_name) > 3:
                    output_file.writelines("Category:," + category+ '\n')
                if len(product_class) > 3:
                    output_file.writelines("Class:," + product_class+ '\n')
                if len(operators) > 3:
                    output_file.writelines("Operators:," + operators+ '\n')
                if len(production) > 2:
                    output_file.writelines("Production (KG):," + production+ '\n')
                if len(turnover) > 3:
                    output_file.writelines("Turn Over (MLN €):," + turnover+ '\n')
                if len(surface) > 3:
                    output_file.writelines("Surface:," + surface+ '\n')


#                if len(volume) > 3:
 #                   output_file.writelines("Volume:," + volume+ '\n')
  #              if len(ingrediants) > 3:
   #                 output_file.writelines("Ingrediants:," + ingrediants+ '\n')
              #  if len(countries_of_origin) > 3:
              #      output_file.writelines("Countries of Origin:," + countries_of_origin+ '\n')
    #            if len(proof) > 3:
     #               output_file.writelines("Proof:," + proof+ '\n')
      #          if len(color) > 3:
       #             output_file.writelines("Colour:," + color+ '\n')


                output_file.writelines('\n')

                if is_door_database_check and is_found_in_doors:

                    if len(doors_name) > 3:
                        output_file.writelines("Name:," + doors_name + '\n')
                    if len(countries_of_origin) > 3:
                        output_file.writelines("Countries of Origin:," + countries_of_origin + '\n')
                    if len(dossier_number) > 3:
                        output_file.writelines("Dossier Number:," + dossier_number + '\n')
                    if len(status) > 3:
                        output_file.writelines("Status:," + status + '\n')
                    if len(application_type) > 3:
                        output_file.writelines("Application Type:," + application_type + '\n')
                    if len(type_of_product):
                        output_file.writelines("Type of Product:," + type_of_product + '\n')
                    if len(date_of_submission) > 3:
                        output_file.writelines("Date of Submission:," + date_of_submission + '\n')
                    if len(date_of_publication) > 3:
                        output_file.writelines("Date of Publication:," + date_of_publication + '\n')
                    if len(date_of_registration) > 3:
                        output_file.writelines("Date of Registration:," + date_of_registration + '\n')
                    if len(producer_group_name) > 3:
                        output_file.writelines("Producer.Group Name:," + producer_group_name + '\n')
                    if len(producer_group_address) > 3:
                        output_file.writelines("Producer.Group Address:," + producer_group_address + '\n')

                    output_file.writelines('\n')

                print("Count:",count)
                count += 1



    return count, not_found_count





if __name__ == '__main__':
    count = 1
    not_found_count = 0
    output_file =  open(os.path.join(HOME_DIR, 'data.csv'), 'a')
    output_file2 = open(os.path.join(HOME_DIR, 'wiki.csv'), 'w')
    output_file.writelines('\n')
    output_file.writelines('\n')
    output_file.writelines('\n')

    pd = get_reading_urls_from_file(os.path.join(HOME_DIR,'urls_list.xlsx'))
    for row in pd.iterrows():
        country_name = row[1][0]
        if country_name not in ["Italy", "France", "Spain","Greece", "Hungary", "germany", "portugal", "austria", "belgium", "luxembourgc"]:
            url = row[1][3]
            count, not_found_count = scrap_url(country_name, url, count, output_file, output_file2, not_found_count)
            print("Not found count: ",not_found_count)


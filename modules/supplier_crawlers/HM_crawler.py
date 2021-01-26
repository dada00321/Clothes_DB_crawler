from lxml import etree
from modules.tier_1_crawler import Tier_1_Crawler

class HM_Crawler(Tier_1_Crawler):
    def __init__(self):
        self.base_url = "https://www2.hm.com"
        
    ''' This func is used by func: extract_data '''
    def __get_genre_list(self):
        return ["女裝","男裝","Divided","童裝"]
    
    ''' This func is used by func: extract_data '''
    def __get_forbidden_big_cat(self):
        return ["檢視全部"]
    
    ''' This func is used by func: generate_tier_1_info '''
    def extract_data(self, supplier_source_path):
        tier_1_info = dict()
        texts = self.load_texts(supplier_source_path)
        if texts:
            html = etree.HTML(texts)
            forbidden_items = self.__get_forbidden_big_cat()
            print("正在清洗資料")
            
            for genre in self.__get_genre_list():
                tier_1_info.setdefault(genre, dict())
                print(f"genre: {genre}")
                #sales_cat_xpath = "//span[contains(text(),'按產品選購')]/../ul/li/a"
                sales_cat_xpath = f"//button[contains(text(),'{genre}')]/../following-sibling::li/span[contains(text(),'按產品選購')]/../ul/li/a"
                tags = html.xpath(sales_cat_xpath)
                tmp_ID = 1
                for tag in tags:
                    sales_cat_text = str(tag.text).strip()
                    if any([forbidden_item in sales_cat_text for forbidden_item in forbidden_items]):
                        continue
                    link = self.base_url + str(tag.get("href")).strip()
                    print(f"{tmp_ID} {sales_cat_text}\n{link}")
                    tier_1_info[genre].setdefault(sales_cat_text, link)
                    tmp_ID += 1
                print()
        return tier_1_info
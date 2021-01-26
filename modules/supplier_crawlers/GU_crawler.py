from lxml import etree
from modules.tier_1_crawler import Tier_1_Crawler

class GU_Crawler(Tier_1_Crawler):
    ''' This func is used by func: extract_data '''
    def __get_genre_list(self):
        return ["women", "men", "kids"]
    
    ''' This func is used by func: extract_data '''
    def __get_forbidden_big_cat(self):
        return ["檢視全部"]
    
    ''' This func is used by func: generate_tier_1_info '''
    def extract_data(self, supplier_source_path):
        tier_1_info = dict()
        texts = self.load_texts(supplier_source_path)
        if texts:
            html = etree.HTML(texts)
            #forbidden_items = self.__get_forbidden_big_cat()
            print("正在清洗資料")
            
            genres = [genre.title() for genre in self.__get_genre_list()]
            tmp_ID = 1
            for genre in genres:
                tier_1_info.setdefault(genre, dict())
                print(f"genre: {genre}")
                common_xpath = f"//div[@id='nav{genre}' and @class='pc']"
                big_cat_xpath = f"{common_xpath}//a[@href='#']"
                tags = html.xpath(big_cat_xpath)
                big_cat_texts = [str(tag.text).strip() for tag in tags]
                for big_cat_text in big_cat_texts:
                    tier_1_info[genre].setdefault(big_cat_text, dict())
                    sales_cat_xpath = f"{common_xpath}//a[contains(text(), '{big_cat_text}') and @href='#']"
                    sales_cat_xpath += "/../following-sibling::*[1]/ul/li/a"
                    #print(f"sales_cat_xpath:\n{sales_cat_xpath}")
                    sub_tags = html.xpath(sales_cat_xpath)
                    
                    for sub_tag in sub_tags:
                        sales_cat_text = str(sub_tag.text).strip()
                        link = sub_tag.get("href")
                        tier_1_info[genre][big_cat_text].setdefault(sales_cat_text, link)
                        print(f"{tmp_ID} {sales_cat_text}")
                        print(f"link: {link}\n")
                        tmp_ID += 1
        return tier_1_info
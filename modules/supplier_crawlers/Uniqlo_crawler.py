from lxml import etree
from modules.tier_1_crawler import Tier_1_Crawler

class Uniqlo_Crawler(Tier_1_Crawler):
    ''' This func is used by func: extract_data '''
    def __get_genre_list(self):
        return ["women","men","kids","baby"]
    
    ''' This func is used by func: extract_data '''
    def __get_forbidden_big_cat(self):
        return ["每週新品","熱門主題","特輯推薦","相關推薦"]
    
    ''' This func is used by func: generate_tier_1_info '''
    def extract_data(self, supplier_source_path):
        tier_1_info = dict()
        texts = self.load_texts(supplier_source_path)
        if texts:
            print("正在清洗資料")
            genres = self.__get_genre_list()
            html = etree.HTML(texts)
            #print(html) # <Element html at 0x24fe65a24c8>
            #print(etree.tostring(html).decode())
            
            for i, genre in enumerate(genres):
                tier_1_info.setdefault(genre, dict())
                common_genre_xpath = f"//a[@id='header_{genre}']/following-sibling::div"
                big_cat_xpath = common_genre_xpath + "//span[@class='title']"
                
                tags = html.xpath(big_cat_xpath)
                big_cat_texts = [str(tag.text.replace("\n", "").strip()) for tag in tags]
                forbidden_items = self.__get_forbidden_big_cat()
                
                new_list = list()
                for big_cat_text in big_cat_texts:
                    if any([forbidden_item in big_cat_text for forbidden_item in forbidden_items]):
                        continue
                    new_list.append(big_cat_text)
                big_cat_texts = new_list
                #print("big_categories:\n", big_cat_texts) 
                
                for big_cat_text in big_cat_texts:
                    if big_cat_text.count(" ") > 1: 
                        big_cat_text = big_cat_text.replace(" ", "")
                    tier_1_info[genre].setdefault(big_cat_text, 
                                                  dict())
                if len(big_cat_texts) == 0:
                    print("({i+1}) {genre} cannot get big_categories.")
                else:
                    for big_catID, big_cat_text in enumerate(big_cat_texts):
                        # mapping: big_category => sales_categories
                        sales_cat_xpath = common_genre_xpath + f"//span[contains(text(),'{big_cat_text}')]"
                        sales_cat_xpath += "/../../li/a[@class='']"
                        sales_cat_tags = html.xpath(sales_cat_xpath)
                        # (1) text of sales_cat
                        sales_cat_texts = list()
                        for tag in sales_cat_tags:
                            tmp = tag.text
                            if "/" in tmp:
                                tmp = ''.join(tmp.split())
                            else:
                                tmp = tmp.replace("\n", "").replace(" ", "").strip()
                            sales_cat_texts.append(tmp)
                                
                        # (2) link of sales_cat
                        sales_cat_links = [tag.get("href").strip() for tag in sales_cat_tags]
                        
                        if (any(sales_cat_texts) or any(sales_cat_links)) and (len(sales_cat_texts) == len(sales_cat_links)):
                            #print("texts:\n", sales_cat_texts)
                            #print("links:\n", sales_cat_links)
                            for i in range(max(len(sales_cat_texts), len(sales_cat_links))):
                                tier_1_info[genre][big_cat_text].setdefault(sales_cat_texts[i], sales_cat_links[i])
                        elif len(sales_cat_texts) != len(sales_cat_links):
                            print("not match!")
                
            print("tier_1_info:")
            print(tier_1_info)
            print("成功產生結果: tier_1_info\n")
            return tier_1_info
        else:
            print("[002] Because func: load_texts has error, cannot execute func: extract_data.")
            return None
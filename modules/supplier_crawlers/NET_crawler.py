from lxml import etree
from modules.tier_1_crawler import Tier_1_Crawler
##########
import os
from modules.base_crawler import Base_Crawler
from modules.other_module.time_helper import countdown

class NET_Crawler(Tier_1_Crawler):
    """
    def __init__(self):
        self.base_url = "https://www.net-fashion.net"
    """
     
    ''' This func is used by func: extract_data '''
    def __get_genre_list(self):
        #return ["女 裝","男 裝","童 裝","Baby 嬰 兒"]
        return ["women","men","kids","baby"]
    
    def __get_genre_links(self):
        genre_links = {"women": "https://www.net-fashion.net/category/1466",
                       "men": "https://www.net-fashion.net/category/1467",
                       "kids": "https://www.net-fashion.net/category/1899",
                       "baby": "https://www.net-fashion.net/category/1038" }
        return genre_links
    
    ''' This func is used by func: extract_data '''
    def __get_forbidden_big_cat(self):
        return ["檢視全部"]
    
    def __get_path_for_genre_source(self, genre):
        supplier_source_path = f"./res/html_source/NET/{genre}_source.txt"
        return supplier_source_path
    
    def get_source_for_genres(self):
        tmp = self.__get_genre_links().items()
        count = 0; size = len(tmp)
        #for genre, link in list(tmp)[2:]:
        for genre, link in tmp:
            print(f"Get source for {genre} ...")
            tool = Base_Crawler()
            source_path = self.__get_path_for_genre_source(genre)
            if os.path.exists(source_path):
                print(f"genre: {genre} 的原始碼已保存")
            else:
                is_soup_saved = tool.save_soup(link, source_path)
                if is_soup_saved:
                    print(f"成功儲存 genre: {genre} 的原始碼\n")
                else:
                    print(f"genre: {genre} 的原始碼儲存失敗\n")
                count += 1
                if count == size: break
                countdown(15)
    
    ''' This func is used by func: generate_tier_1_info '''
    def extract_data(self):
        tier_1_info = dict()
        #texts = self.load_texts(supplier_source_path)
        #if texts:
        #html = etree.HTML(texts)
        #forbidden_items = self.__get_forbidden_big_cat()
        print("正在清洗資料")
        
        #tmp_ID = 1
        for genre, link in self.__get_genre_links().items():
        #for i, genre in enumerate(self.__get_genre_list()):
            tier_1_info.setdefault(genre, dict())
            
            print(f"genre: {genre}")
            source_path = self.__get_path_for_genre_source(genre)
            if os.path.exists(source_path):
                texts = self.load_texts(source_path)
                html = etree.HTML(texts)
                partial_link = "/".join(link.split("/")[-2:])
                common_xpath = f"//li/a[contains(@href,'{partial_link}')]/../.."
                if genre in ["women","men"]:
                    big_cat_xpath = common_xpath + "//a/b"
                    ###
                    tags = html.xpath(big_cat_xpath)
                    big_cat_texts = [tag.text.strip().replace("。","") for tag in tags if "．任選" not in tag.text]
                    print(big_cat_texts, "\n")
                    #--------------------
                    tmp_count = 1
                    for big_cat_text in big_cat_texts:
                        tier_1_info[genre].setdefault(big_cat_text, dict())
                        
                        base_path = f"//a/b[contains(text(),'{big_cat_text}')]"
                        ancestor_xpath = common_xpath + f"{base_path}/../../.."
                        ancestor_tag = html.xpath(ancestor_xpath)[0].tag
                        #print(ancestor_tag) # div: 有sales_cat / ul: 無sales_cat
                        ''' 若有細項(sales_cat),不記錄 big_cat鏈結 => 找到底下所有細項再記錄 sales_cat鏈結
                            反之, 只記錄 big_cat鏈結
                        '''
                        if ancestor_tag == "div":
                            link_xpath = f"{base_path}/../../..//a[contains(text(),'。')]"
                            tags = html.xpath(link_xpath)
                            sales_cat_names = [str(tag.text).strip().replace("。","") for tag in tags]
                            sales_cat_links = [tag.get("href") for tag in tags]
                            # if any("View All" in name for name in sales_cat_names):
                            
                            for i, text in enumerate(sales_cat_names):
                                if "View All" in text:
                                    del sales_cat_names[i], sales_cat_links[i]
                                #####
                                tier_1_info[genre][big_cat_text].setdefault(sales_cat_names[i], 
                                                                            sales_cat_links[i])
                            print(f"   ({tmp_count}) sales_cat_names:\n{sales_cat_names}", sep='')
                            print(f"links:\n{sales_cat_links}\n", sep='')
                            
                        elif ancestor_tag == "ul":
                            link_xpath = f"{base_path}/.."
                            link = html.xpath(link_xpath)[0].get("href")
                            print(f"   ({tmp_count}) link:", link, "\n")
                            
                            tier_1_info[genre][big_cat_text].setdefault("big_cat_link", link)
                            
                        tmp_count += 1
                else:
                    print("==="*5)
                    ''' genre: kids 和 baby 因為皆無 sales_cat，故直接抓 big_cat的文字、鏈結即可
                    '''
                    #big_cat_xpath = common_xpath + "//a[@class='no2sl']"
                    if genre == "kids":
                        big_cat_types = {"女童": "kids_girl", "男童":"kids_boy"}
                    elif genre == "baby":
                        big_cat_types = {"女嬰": "baby_girl", "男嬰":"baby_boy"}
                    for big_cat_type, new_genre in big_cat_types.items():
                        tier_1_info[genre].setdefault(new_genre, dict())
                        
                        big_cat_xpath = f"//b[contains(text(),'{big_cat_type}')]/../../following-sibling::li/a"
                        ####
                        tags = html.xpath(big_cat_xpath)
                        big_cat_texts = [tag.text.strip().replace("。","") for tag in tags if "．任選" not in tag.text]
                        big_cat_links = [tag.get("href") for tag in tags]
                        print("new genre:", new_genre)
                        for big_cat_text, big_cat_link in zip(big_cat_texts, big_cat_links):
                            tier_1_info[genre][new_genre].setdefault(big_cat_text, big_cat_link)
                            print(f"big_cat: {big_cat_text}\nlink:{big_cat_link}\n")
                        '''
                        for big_cat_text in big_cat_texts:
                            sales_cat_xpath = big_cat_xpath + f"[contains(text(),'{big_cat_text}')]"
                        '''
                        print()
                        
                #tags = html.xpath(big_cat_xpath)
                #big_cat_texts = [tag.text.strip() for tag in tags if "系列" not in tag.text]
                #print(big_cat_texts)
                print()
                
                '''
                big_cat_xpath = "//a/b"
                tags = html.xpath(big_cat_xpath)
                big_cat_texts = [tag.text.strip() for tag in tags]
                print(big_cat_texts)
                '''
            else:
                print("[009] Error occurs!")
                
        return tier_1_info
''' Get suppliers' html source code '''
import requests as rs
from bs4 import BeautifulSoup as bs
from lxml import etree
import json 
import os

''' This func is used by func: generate_tier_1_info
                         func: delete_tier_1_temp_files
'''
def get_two_saving_path(original_supplier_name):
    supplier_source_path = f"./res/html_source/{original_supplier_name}_source.txt"
    tier_1_info_path = f"./output/tier1/{original_supplier_name}_tier_1_info.json"
    return supplier_source_path, tier_1_info_path

''' This func is used by outer programs '''
def generate_tier_1_info(original_url, original_supplier_name):
    supplier_source_path, tier_1_info_path = get_two_saving_path(original_supplier_name)
    print(supplier_source_path)
    print(tier_1_info_path)
    print(original_url)
    is_soup_saved = save_soup(original_url, supplier_source_path)
    if is_soup_saved == True:
        # tier_1_info: (<type: dict>)
        tier_1_info = extract_data(supplier_source_path)
        if tier_1_info:
            save_json(tier_1_info_path, tier_1_info) # dict -> json
        else: 
            print("Because func: extract_data has error, cannot execute func: generate_tier_1_info.")
    else:
        print("[001] Because func: save_soup has error, cannot execute other func below.")

def delete_tier_1_temp_files(original_supplier_name):
    supplier_source_path, _ = get_two_saving_path(original_supplier_name)
    if os.path.exists(supplier_source_path):
        while True:
            keyin = str(input(f"確定要刪除: {supplier_source_path} 嗎？\n請輸入(y/n)並按下Enter ==> "))
            if keyin.lower() == "y":
                os.remove(supplier_source_path)
                print("暫存資料刪除成功！")
                break
            elif keyin.lower() == "n":
                print("OK!操作取消")
                break
            else:
                print("輸入錯誤，請重新輸入！")
    else:
        print("[006] Fail to remove temporary file.(The path does not exist.)")
    
def __get_genre_list():
    return ["women","men","kids","baby"]

def __get_forbidden_big_cat():
    return ["每週新品","熱門主題","特輯推薦","相關推薦"]

def load_texts(supplier_source_path):
    string_buffer = None
    with open(supplier_source_path, "r", encoding="utf-8") as fp:
        texts = fp.readlines()
        string_buffer = ""
        for row in texts:
            if "<br/>" in row:
                row = row.replace("<br/>", "")
                row = row.replace("\n", "")
            string_buffer += row
        #texts = ''.join(texts)
    #return texts
    return string_buffer
    
def extract_data(supplier_source_path):
    tier_1_info = dict()
    texts = load_texts(supplier_source_path)
    if texts:
        print("正在清洗資料")
        genres = __get_genre_list()
        html = etree.HTML(texts)
        #print(html) # <Element html at 0x24fe65a24c8>
        #print(etree.tostring(html).decode())
        
        for i, genre in enumerate(genres):
            tier_1_info.setdefault(genre, dict())
            common_genre_xpath = f"//a[@id='header_{genre}']/following-sibling::div"
            big_cat_xpath = common_genre_xpath + "//span[@class='title']"
            
            tags = html.xpath(big_cat_xpath)
            big_cat_texts = [str(tag.text.replace("\n", "").strip()) for tag in tags]
            forbidden_items = __get_forbidden_big_cat()
            
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

''' Only can be used by two functions: (1) save_soup and (2) save_json '''
def __save_file(saving_path, saving_obj, saving_type):
    ''' prepare env for saving file '''
    path = saving_path[:]
    tmp = path.split("/")
    if str(path[:2]) != "./":
        path = "./" + path
    for i in range(2, len(tmp)):
        curr_path = "/".join(tmp[1:i])
        if not os.path.exists(curr_path):
            os.mkdir(curr_path)
                
    ''' saving file '''
    try:
        with open(saving_path, "w", encoding="utf-8") as fp:
            if saving_type == "soup":
                # saving_obj: soup_obj
                alias_file_name = "網頁原始碼"
                fp.write(saving_obj.prettify())
            elif saving_type == "json":
                # saving_obj: dict_obj
                alias_file_name = "json檔案"
                json.dump(saving_obj, fp, ensure_ascii=False)
        print(f"{alias_file_name}寫入成功!\n")
        return True
    except: 
        func_name = f"save_{saving_type}"
        err_msg = f"[004] Fail to execute func: {func_name}"
        err_msg += f"\n（{alias_file_name}寫入失敗）\n"
        print(err_msg)
        return False
            
''' This func is used by func: generate_tier_1_info '''
def save_json(saving_path, dict_obj):
    _ = __save_file(saving_path = saving_path,
                  saving_obj = dict_obj,
                  saving_type = "json")
    del _
    
''' This func is used by func: generate_tier_1_info '''
def save_soup(original_url, supplier_source_path):
    save_status = None
    try:
        print("正在抓取網頁原始碼")
        url = "http://webcache.googleusercontent.com/search?q=cache:"
        url += original_url
        resp = rs.get(url)
        if resp.status_code == rs.codes.ok:
            resp.encoding = "utf-8"
            soup = bs(resp.text, "lxml")
            save_status = __save_file(saving_path = supplier_source_path,
                                    saving_obj = soup,
                                    saving_type = "soup")
        else:
            print("[005] Fail to get response.")
    except: 
        print("[003] Error occurs! ('save_soup')")
    finally:
        return save_status
    
if __name__ == "__main__":
    original_url = "https://www.uniqlo.com/tw"
    original_supplier_name = "UNIQLO"
    
    #generate_tier_1_info(original_url, original_supplier_name)
    delete_tier_1_temp_files(original_supplier_name)
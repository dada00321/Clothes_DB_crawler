import os
from modules.base_crawler import Base_Crawler
from modules.csv_module.csv_helper import read_clothDB_info

class Tier_1_Crawler(Base_Crawler):
    ''' This func is used by func: generate_tier_1_info
                             func: delete_tier_1_temp_files
    '''
    def get_two_saving_paths(self, original_supplier_name):
        supplier_source_path = f"./res/html_source/{original_supplier_name}_source.txt"
        tier_1_info_path = f"./output/tier1/json/{original_supplier_name}_tier_1_info.json"
        return supplier_source_path, tier_1_info_path
    
    ''' This func is used by main_DB_crawler.py 
        input data: suppliers' names and URLs is obtained from outer csv module.
    '''
    # Rewrite from func: generate_tier_1_info,
    # only get all html sources and save them to specific path.
    def get_soups_for_suppliers(self):
        supplier_names, supplier_URLs = read_clothDB_info()
        ID_counter = 1
        for original_supplier_name, original_url in zip(supplier_names, supplier_URLs):
            supplier_source_path, _ = self.get_two_saving_paths(original_supplier_name)
            is_soup_saved = self.save_soup(original_url, supplier_source_path)
            if is_soup_saved:
                print(f"成功儲存第{ID_counter}家服飾商:{original_supplier_name}的原始碼\n")
            else:
                print(f"第{ID_counter}家服飾商:{original_supplier_name}的原始碼儲存失敗\n")
            ID_counter += 1
    
    ''' This func is used by main_DB_crawler.py
        [Just for testing if errors occur]
        input data: is given by function parameter
    '''
    def get_soup_for_one_supplier(self, supplier_name, original_url):
        print(f"開始抓取服飾商: {supplier_name} 的網頁原始碼")
        cw = Tier_1_Crawler()
        supplier_source_path, _ = cw.get_two_saving_paths(supplier_name)
        save_status = cw.save_soup(original_url, supplier_source_path)
        if save_status == False:
            print("[008] Error occurs! (func: get_soup_for_one_supplier)")
    
    ''' This func is used by main_DB_crawler.py '''
    def generate_tier_1_info(self, supplier_name, method=None):
        supplier_source_path, tier_1_info_path = self.get_two_saving_paths(supplier_name)
        if os.path.exists(supplier_source_path):
            # tier_1_info: (<type: dict>)
            if method == None:
                tier_1_info = self.extract_data(supplier_source_path)
            elif method == "NET-only":
                tier_1_info = self.extract_data()
            
            if tier_1_info:
                try:
                    self.save_json(tier_1_info_path, tier_1_info) # dict -> json
                    print(f"成功儲存服飾商: {supplier_name} 的 tier_1_info (json檔)")
                except:
                    print("[007] Cannot save tier_1_info.")
            else: 
                print("Because func: extract_data has error, cannot execute func: generate_tier_1_info.")
        else:
            print("[001] Because func: save_soup has error, cannot execute other func below.")
        
    ''' This func is used by main_DB_crawler.py '''
    def delete_tier_1_temp_files(self, supplier_name):
        supplier_source_path, tier_1_info_path = self.get_two_saving_paths(supplier_name)
        if os.path.exists(tier_1_info_path):
            while True:
                keyin = str(input(f"確定要刪除: {tier_1_info_path} 嗎？\n請輸入(y/n)並按下Enter ==> "))
                if keyin.lower() == "y":
                    os.remove(tier_1_info_path)
                    print("暫存資料刪除成功！")
                    break
                elif keyin.lower() == "n":
                    print("OK!操作取消")
                    break
                else:
                    print("輸入錯誤，請重新輸入！")
        else:
            print("[006] Fail to remove temporary file.(The path does not exist.)")
    
    ''' This func is used by func: extract_data '''
    def load_texts(self, source_path):
        string_buffer = None
        with open(source_path, "r", encoding="utf-8") as fp:
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
import requests
from bs4 import BeautifulSoup
import json 
import os
import time

class Base_Crawler():
    ''' Only can be used by two functions: (1) save_soup and (2) save_json '''
    def __save_file(self, saving_path, saving_obj, saving_type):
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
            print(f"{alias_file_name}寫入成功!")
            return True
        except: 
            func_name = f"save_{saving_type}"
            err_msg = f"[004] Fail to execute func: {func_name}"
            err_msg += f"\n（{alias_file_name}寫入失敗）\n"
            print(err_msg)
            return False
                
    ''' This func is used by func: generate_tier_1_info '''
    def save_json(self, saving_path, dict_obj):
        _ = self.__save_file(saving_path = saving_path,
                      saving_obj = dict_obj,
                      saving_type = "json")
        del _
    
    ''' This func is used by func: generate_tier_1_info '''
    def save_soup(self, original_url, source_path):
        save_status = None
        try:
            print("正在抓取網頁原始碼")
            url = "http://webcache.googleusercontent.com/search?q=cache:"
            if "us" not in original_url:
                visiting_url = url + original_url
            else:
                visiting_url = original_url
            print("等待三秒")
            time.sleep(3)
            resp = requests.get(visiting_url)
            if resp.status_code == requests.codes.ok:
                resp.encoding = "utf-8"
                soup = BeautifulSoup(resp.text, "lxml")
                save_status = self.__save_file(saving_path = source_path,
                                               saving_obj = soup,
                                               saving_type = "soup")
            else:
                print("[005] Fail to get response.")
        except: 
            print("[003] Error occurs! ('save_soup')")
        finally:
            return save_status
from modules.supplier_info.supplier_info_collector import Supplier_Info_Collector
from modules.tier_1_crawler import Tier_1_Crawler
from modules.supplier_crawlers.Uniqlo_crawler import Uniqlo_Crawler
from modules.supplier_crawlers.HM_crawler import HM_Crawler
from modules.supplier_crawlers.GU_crawler import GU_Crawler
from modules.supplier_crawlers.NET_crawler import NET_Crawler
from modules.csv_module.csv_helper import json_to_csv

class Main_DB_Crawler():
    def collect_info_for_suppliers(self, supplier_chart):
        suppliers_txt_path = "./res/DB_list/DB_chart.txt"
        col_names = ["排名","台灣服飾廠商","URL"]
        saving_path = "./res/DB_list/clothDB_info.csv"
        
        recorder = Supplier_Info_Collector(supplier_chart, suppliers_txt_path, col_names, saving_path)
        recorder.save_DB_chart_csv()
        
    def set_supplier_name(self, supplier_name):
        self.supplier_name = supplier_name
        
    def call_get_soups_for_suppliers(self):
        tier_1_cw = Tier_1_Crawler()
        tier_1_cw.get_soups_for_suppliers()
    
    def filtering_Uniqlo(self):
        self.set_supplier_name("UNIQLO")
        uq_crawler = Uniqlo_Crawler()
        uq_crawler.generate_tier_1_info(self.supplier_name)
        #uq_crawler.delete_tier_1_temp_files(self.supplier_name)
    
    def filtering_HM(self):
        self.set_supplier_name("H&M")
        hm_crawler = HM_Crawler()
        hm_crawler.generate_tier_1_info(self.supplier_name)
        #hm_crawler.delete_tier_1_temp_files(self.supplier_name)
        
    def filtering_GU(self):
        self.set_supplier_name("GU")
        gu_crawler = GU_Crawler()
        gu_crawler.generate_tier_1_info(self.supplier_name)
        #gu_crawler.delete_tier_1_temp_files(self.supplier_name)
    
    def filtering_NET(self):
        self.set_supplier_name("NET")
        net_crawler = NET_Crawler()
        # net_crawler.get_source_for_genres()
        # net_crawler.extract_data()
        net_crawler.generate_tier_1_info(self.supplier_name, method="NET-only")
        #net_crawler.delete_tier_1_temp_files(self.supplier_name)
    
if __name__ == "__main__":
    ####################################################
    # Collect csv information for all suppliers.
    # => Collect by visiting all possible websites for suppliers,
    #    then save info to the csv file.
    ####################################################
    # 流程
    # 儲存路徑: ./res/DB_list/clothDB_info.csv
    # 需要自行調整、刪去抓下網址的 redundency
    # 並在同一目錄下另存一個 final_clothDB_info.csv
    """
    cw = Main_DB_Crawler()
    supplier_chart = ["UNIQLO","H&M","GU","GAP","ZARA","CACO",
                      "NET","BENETOON","Forever 21","GIORDANO"]
    cw.collect_info_for_suppliers(supplier_chart)
    """
    ####################################################
    # Get all html sources. (txt files)
    ####################################################
    
    # 流程
    #   抓取 res/DB_list/final_clothDB_info.csv 目錄下各服飾商的 html sources
    #   並逐一保存到 res/html_source
    """
    cw = Main_DB_Crawler()
    cw.call_get_soups_for_suppliers()
    """
    
    ####################################################
    # Extract data, and save tier_1_info as "json" and "csv" files.
    ####################################################
    # 流程
    # 1.過濾html source並將結果以json檔保存
    # 儲存路徑: ./output/tier1/json
    cw = Main_DB_Crawler()
    cw.filtering_Uniqlo()
    cw.filtering_HM()
    cw.filtering_GU()
    cw.filtering_NET()
    # 2.讀取存放json檔目錄下的所有檔案，並轉為csv檔保存
    # 儲存路徑: ./output/tier1/csv
    json_to_csv()
    
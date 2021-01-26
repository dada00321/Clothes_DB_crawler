import pandas as pd
import os

def read_clothDB_info():
    ''' for here '''
    #path_ = "../../res/DB_list/final_clothDB_info.csv"
    ''' for main DB crawler '''
    path_ = "./res/DB_list/final_clothDB_info.csv"
    df = pd.read_csv(path_)
    return df["台灣服飾廠商"], df["URL"]

###########################################

def get_uniform_csv_colume_names():
    return ["genre","category","sales-category","link","sales-category ID"]

def get_supplier_name(json_file_name):
    supplier_name = json_file_name.split("_")[0]
    #print(f"supplier_name: {supplier_name}")
    return supplier_name

def generate_salesID_prefix(supplier_name, supplier_names):
    # 001, 002, 003, etc.
    salesID_prefix = "{:03d}".format(supplier_names.index(supplier_name)+1)
    return salesID_prefix

def generate_salesID_suffix(link_count):
    return "{:04d}".format(link_count)

def create_csv_env():
    # tier-1 csv env.
    ''' for main DB crawler '''
    dest_path = "./output/tier1/csv"
    for i in range(2, len(dest_path.split("/"))+1):
        curr_path = "/".join(dest_path.split("/")[1:i])
        if not os.path.exists(curr_path):
            print(f"成功建立目錄: {curr_path}")
            os.mkdir(curr_path)
    return dest_path
    
def json_to_csv():
    # In order to generate "sales-category ID" 
    # to save in csv file, read suppliers data firstly.
    supplier_names, _ = read_clothDB_info()
    supplier_names = list(supplier_names)
    
    # Setting output_dict
    col_names = get_uniform_csv_colume_names()
    output_dict = dict()
    for col_name in col_names:
        output_dict.setdefault(col_name, list())
    
    # Read json file and extract as a dict for each record
    ''' for here '''
    #path_ = "../../output/tier1/"    
    ''' for main DB crawler '''
    path_ = "./output/tier1/json/"
    
    test_dict = {"set_1": [0,2,3],
                 "set_2": [1]
                }
    json_files = os.listdir(path_)
    #for fp in json_files[test_ID:(test_ID+1)]:
    for test_num, fp in enumerate(json_files):
        #try:
        full_path = path_ + fp
        #if os.path.isfile(full_path):
        #if test_num in test_dict.get("set_1"):
        ''' 清空 output_dict 的 values'''
        for col_name in col_names:
            output_dict[col_name] = list()
    
        #print(f"json file: {fp}")
        supplier_name = get_supplier_name(fp)
        salesID_prefix = generate_salesID_prefix(supplier_name, supplier_names)
        
        data = pd.read_json(full_path, encoding="utf-8-sig")
        data = dict(data)
        link_count = 0
        
        curr_dict = dict()
        for genre, tmp in data.items():
            for big_cat, tmp2 in tmp.items():
                # 若為第一種 json格式(with "sales_cat")
                if test_num in test_dict.get("set_1"):
                    #print("\n", genre, sep="")
                    curr_dict["genre"] = genre.upper()
                    #print(big_cat)
                    curr_dict["category"] = big_cat
                    if type(tmp2).__name__=="dict":
                        for sales_cat, link in tmp2.items():
                            #print(f"   {sales_cat}")
                            curr_dict["sales-category"] = sales_cat
                            #print(f"      {link}")
                            curr_dict["link"] = link
                            link_count += 1
                            #curr_dict["sales-category ID"] = link_count
                            salesID = salesID_prefix + generate_salesID_suffix(link_count)
                            curr_dict["sales-category ID"] = salesID
                            for col_name in col_names:
                                output_dict[col_name].append(curr_dict[col_name])
                
                # 若為第二種 json格式(without "sales_cat")
                elif test_num in test_dict.get("set_2"):
                    if type(tmp2).__name__=="float":
                        continue
                    elif type(tmp2).__name__=="str":
                        link = tmp2
                        #print("\n", genre, sep="")
                        curr_dict["genre"] = genre.upper()
                        #print(big_cat)
                        curr_dict["category"] = big_cat
                        #print(f"   {sales_cat}")
                        curr_dict["sales-category"] = None
                        #print(f"      {link}")
                        curr_dict["link"] = link
                        link_count += 1
                        curr_dict["sales-category ID"] = salesID_prefix + generate_salesID_suffix(link_count)
                        for col_name in col_names:
                            output_dict[col_name].append(curr_dict[col_name])
        #print(output_dict)
        #print(f"link_count: {link_count}")
        
        # Save the output_dict as a csv file
        df = pd.DataFrame(output_dict, columns= col_names)
        csv_path = create_csv_env()
        df.to_csv(f"{csv_path}/{supplier_name}_tier_1.csv", encoding="utf-8-sig", index=False, header=True)
        print(f"成功將供應商:{supplier_name} json檔 轉為 csv檔保存！\n")
        
        #except:
            #print(f"供應商:{supplier_name} csv檔保存失敗\n")
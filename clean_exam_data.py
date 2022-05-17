import json
from urllib.parse import parse_qs
from datetime import datetime
import pandas as pd

"""
此 py 檔用來清洗雲端大師 Line 機器人的 Log
將會清洗出：
    答題時間 (timestamp)
        timestamp，ex. 1651034255138
    line_user_id
        userId， ex. U8a07664bc0d08dd21456706a1bb8527a
    email，若無則回傳 ' '
        user_email，ex. abc123@hotmail.com
    答題題號
        question_id，ex. 288
    該題正解
        true_ans，ex. A
    用戶答題
        this_ans，ex. D
"""
# 開 json 檔
with open("downloaded-logs-20220512-192952.json", "r", encoding="utf-8") as file:
    # 取出 json 檔
    jsonObject = json.load(file)
    # 關檔案
    file.close()

# 測試是否有開啟，查看有幾筆 
# print(len(jsonObject)) # 1751

# 查看類型
# print(type(jsonObject)) # list
# i = 0 # 用來計算出現次數

# 定義一個清單，等等用來塞過濾好的資料
_list = []

# 迴圈取出要的資料，有 1751 則 log
for log in jsonObject: # 外迴圈
    # 要再迴圈取出 events 中的事件
    for event in log["jsonPayload"]["events"]: # 內迴圈
        # 每個 event 為一個用戶動作的事件, 需要判別是什麼動作
        # 我們需要保存的動作事件為 postback 事件
        if event["type"] != "postback":
            # 如果不是 postback 事件，就跳過
            continue
        if event["postback"]["data"].startswith("function=practice_answer"):
            # 如果開頭為 function=practice_answer

            line_user_id = event["source"]["userId"] # line 用戶 id
            test_time = event["timestamp"] # 觸發這個答題
            
            # 解析 postback 的 data，parse_qs 
            # 這個方法可以將 "A=abc&B=123&C=164&C=555a" 這種長相的字串轉換成字典 <String, List<String>>
            # => {'A': ['abc'], 'B': ['123'], 'C': ['164', '555a']}
            postback_data_dict = parse_qs(event["postback"]["data"]) 

            table_name = postback_data_dict.get("table_name")[0] # 考題科目表
            question_id = postback_data_dict.get("question_id")[0] # 考題題號
            this_ans = postback_data_dict.get("this_ans")[0] # 用戶答的題目
            true_ans = postback_data_dict.get("true_ans")[0]
            user_email = postback_data_dict.get("user_email", [" "])[0]
            
            # 查看一下
            # print(line_user_id)
            # print(test_time)
            # print(type(test_time)) # int
            # print(table_name)
            # print(question_id)
            # print(this_ans)
            # print(true_ans)
            # print(f"email: {user_email}")
            # i += 1
            # print(i)

            # # 將資料放入一個字典
            d = {
                "line_user_id": line_user_id,
                "test_time": datetime.fromtimestamp(test_time/1000.0), # 將測驗時間轉換成 datetime 類型 1651034512861 => 
                "test_subject_table": table_name,
                "question_id": question_id,
                "choose_answere": this_ans,
                "true_answere": true_ans,
                "user_email": user_email
            }
            # 將字典放入清單 _list
            _list.append(d)

            break # events 內最多只有一個 postback 為 function=practice_answer # 因此可以直接 break 內迴圈，避免運算

# 將 _list 轉換成 csv
df = pd.json_normalize(_list)

df.to_csv("test.csv")
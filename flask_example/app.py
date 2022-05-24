
from flask import Flask, send_file
import os
import pandas as pd
import json
from urllib.parse import parse_qs
from datetime import datetime

"""
此 py 檔案用來作為一個簡易的伺服器
當用戶發出 <網址>/qa_statistic 要求時
我們就給他整理好的 csv
"""

app = Flask(__name__)

@app.route('/') # 測試用路由
def index():
    return 'Hello World!'

@app.route('/qa_statistic', methods=["GET"])
def qa_statistic():
    try:
    
        # 將前幾天寫的程式碼貼過來而已，註解可以從前兩天寫的 py 檔案找到
        with open("downloaded-logs-20220512-192952.json", "r", encoding="utf-8") as file:
            jsonObject = json.load(file)
            file.close()
        _list = []
        for log in jsonObject: 
            for event in log["jsonPayload"]["events"]:
                if event["type"] != "postback":
                    continue
                if event["postback"]["data"].startswith("function=practice_answer"):
                    line_user_id = event["source"]["userId"] 
                    test_time = event["timestamp"]
                    postback_data_dict = parse_qs(event["postback"]["data"]) 
                    table_name = postback_data_dict.get("table_name")[0] 
                    question_id = postback_data_dict.get("question_id")[0] 
                    this_ans = postback_data_dict.get("this_ans")[0] 
                    true_ans = postback_data_dict.get("true_ans")[0]
                    user_email = postback_data_dict.get("user_email", [" "])[0]
                    d = {
                    "line_user_id": line_user_id,
                    "test_time": datetime.fromtimestamp(test_time/1000.0), # 將測驗時間轉換成 datetime 類型 1651034512861 => 
                    "test_subject_table": table_name,
                    "question_id": question_id,
                    "choose_answere": this_ans,
                    "true_answere": true_ans,
                    "user_email": user_email
                        }
                    _list.append(d)

        df = pd.json_normalize(_list)
        # df.to_csv("test.csv", index=False)
        df = df.filter(items=["test_subject_table", "question_id", "choose_answere", "true_answere"])
        test_popu_table = df.groupby(["test_subject_table", "question_id"]).size().to_frame('test_population').reset_index()
        df = df.groupby(["test_subject_table", "question_id", "choose_answere", "true_answere"]).size().to_frame('count').reset_index()
        df.loc[df["choose_answere"] == "A", "choose_a_population"] = df["count"]
        df.loc[df["choose_answere"] == "B", "choose_b_population"] = df["count"]
        df.loc[df["choose_answere"] == "C", "choose_c_population"] = df["count"]
        df.loc[df["choose_answere"] == "D", "choose_d_population"] = df["count"]
        df = df.merge(test_popu_table)
        del df["choose_answere"]
        del df["count"] 
        df = df.set_index(["test_subject_table", "question_id","true_answere", "test_population"]).stack().unstack().sort_values(ascending=False, by="test_population")
        df = df.fillna(0).astype(int, errors = 'ignore')
        df = df.reset_index()
        df["choose_a_probability"] = df["choose_a_population"] / df["test_population"]
        df["choose_b_probability"] = df["choose_b_population"] / df["test_population"]
        df["choose_c_probability"] = df["choose_c_population"] / df["test_population"]
        df["choose_d_probability"] = df["choose_d_population"] / df["test_population"]
        df.loc[df["true_answere"] == "A", "correct_rate"] = df["choose_a_population"]/df["test_population"]
        df.loc[df["true_answere"] == "B", "correct_rate"] = df["choose_b_population"]/df["test_population"]
        df.loc[df["true_answere"] == "C", "correct_rate"] = df["choose_c_population"]/df["test_population"]
        df.loc[df["true_answere"] == "D", "correct_rate"] = df["choose_d_population"]/df["test_population"]
        # df.to_csv("/tmp/arrange.csv", index=False)
        df = df.dropna()
        df.to_excel("/tmp/arrange.xlsx", sheet_name = "Data", index = False)

        return send_file('/tmp/arrange.xlsx', as_attachment=True)
    except:
        return {"message": "System Error"}, 500 # http status code

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=os.environ['DEBUG'])
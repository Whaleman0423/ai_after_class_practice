import pandas as pd

"""
此 py 檔用來將已經清洗出的答題資料整理成合乎考題統計邏輯的的資料

原 test.csv 含有 7 個欄位：
    line_user_id
        用戶 id (Str)

    test_time
        測驗時間 (Datetime)

    test_subject_table,
        考題科目表 (Str)

    question_id,
        考題題號 (Str)

    choose_answere,
        用戶選擇的選項 (Str)

    true_answere,
        此題答案 (Str)

    user_email
        用戶 email (Str)


預計整理成 13 個欄位：
    subject_table
        題目科目 (Str)
    
    question_id
        題號 (Str)
    
    true_answere
        正確答案 (Str)
    
    test_population
        答題人數 (int)

    choose_a_population
        選 A 的人數 (int)

    choose_b_population
        選 B 的人數 (int)

    choose_c_population
        選 C 的人數 (int)

    choose_d_population
        選 D 的人數 (int)

    choose_a_probability
        答 A 的機率 (float)

    choose_b_probability
        答 B 的機率 (float)

    choose_c_probability
        答 C 的機率 (float)
    
    choose_d_probability
        答 D 的機率 (float)

    correct_rate    
        答對率 (float)
"""

# 使用 pandas 打開 csv
df = pd.read_csv("test.csv")
# # 印出來看看
# print(df)

# 我們需要的欄位為 題目表、題號、用戶選擇的選項、此題答案
# 使用 dataframe 的 filter 篩選出我們要的欄位，並取代舊的 df
df = df.filter(items=["test_subject_table", "question_id", "choose_answere", "true_answere"])
# # 印出來看看
# print(df)

# 為了取得 test_population(答題人數)
# 使用 groupby 功能，它的功能可以將 dataframe 的所有列，依照所選的欄位去分組(group)
# 以題目科目表、題號為欄位分組區分，將會分出該組出現 row 的次數，此處建議依照下方一個個分別 print 出來比較好理解
# print(df.groupby(["test_subject_table", "question_id"]).size())
# print(df.groupby(["test_subject_table", "question_id"]).size().to_frame('test_population')) # to_frame 為出現的次數欄給予欄位名
# print(df.groupby(["test_subject_table", "question_id"]).size().to_frame('test_population').reset_index()) # 由於 groupby 會自動以欄位為索引(index)，因此需 reset

test_popu_table = df.groupby(["test_subject_table", "question_id"]).size().to_frame('test_population').reset_index() # 放進 test_popu_table 這個變數
# 印出來看看
# print(test_popu_table)

# 同理，因為我們要記錄一題中選A、選B...的各別有幾人，因此需再增加 choose_answere 為分組的依據，
# 加入 true_answere 是因為要保留該欄位，且加入它不會影響到分組，印出來看看
# print(df.groupby(["test_subject_table", "question_id", "choose_answere"]).size().to_frame('count').reset_index())
# print(df.groupby(["test_subject_table", "question_id", "choose_answere", "true_answere"]).size().to_frame('count').reset_index())
# sort_values(ascending=False) 可以用來將列排序，ascending=False 意思是反過來，由大到小
# print(df.groupby(["test_subject_table", "question_id", "choose_answere", "true_answere"]).size().to_frame('count').reset_index().sort_values(ascending=False, by="count"))

# 將 df 以題目表、題號、用戶選擇的選項分組
df = df.groupby(["test_subject_table", "question_id", "choose_answere", "true_answere"]).size().to_frame('count').reset_index()
# 印出來看看
# print(df)

# 將用戶所選的選項紀錄正規化，請去查詢什麼叫資料庫正規化並且它又分為哪幾種，有什麼差別
# df.loc 可以製造假設式，當 choose_answere 為 A，則 choose_a_population 為 該 group 出現的次數，以下 B、C、D 以此類推
df.loc[df["choose_answere"] == "A", "choose_a_population"] = df["count"]
df.loc[df["choose_answere"] == "B", "choose_b_population"] = df["count"]
df.loc[df["choose_answere"] == "C", "choose_c_population"] = df["count"]
df.loc[df["choose_answere"] == "D", "choose_d_population"] = df["count"]
# 印出來看看
# print(df)
# print(df.sort_values(ascending=False, by="count"))

# 將 df 與 test_popu_table 組合在一起
df = df.merge(test_popu_table)
# 印出來看看
# print(df)
# print(test_popu_table)
# print(test_popu_table.sort_values(ascending=False, by="test_population")) # 練習最多次的題目 505 440 119 253 430
# print(df.sort_values(ascending=False, by="test_population"))

# 由於已經取出正規化後 用戶的選項，以及不需要 count 欄位，因此可以去除 choose_answere、count 兩個欄位
del df["choose_answere"]
del df["count"]
# 印出來看看
# print(df)

# 將同題目表、題號的 row 結合，以下的程式碼是查出來的，有興趣的同學可以查閱 stack 或 unstack 的方法
# 搜尋的關鍵字: dataframe merge rows NaN groupby based on 2 index itself
# https://stackoverflow.com/questions/40411474/merge-rows-in-dataframe-by-removing-nans-after-groupby
df = df.set_index(["test_subject_table", "question_id","true_answere", "test_population"]).stack().unstack().sort_values(ascending=False, by="test_population")
# 印出來看看
# print(df)

# 將 Nan 以 0 補足並定義欄位的值須為 int，errors = 'ignore'為當遇到錯誤，直接忽略，因為字串不能轉成整數
df = df.fillna(0).astype(int, errors = 'ignore')
# 印出來看看
# print(df)

# 解除索引欄位
# df = df.reset_index(["test_subject_table", "question_id","true_answere", "test_population"])
df = df.reset_index()
# 印出來看看
# print(df)

# 選項的機率欄位
df["choose_a_probability"] = df["choose_a_population"] / df["test_population"]
df["choose_b_probability"] = df["choose_b_population"] / df["test_population"]
df["choose_c_probability"] = df["choose_c_population"] / df["test_population"]
df["choose_d_probability"] = df["choose_d_population"] / df["test_population"]
# 印出來看看
# print(df)

# 如果正解為 A，則取選 A 的數除以答題總次數，即為答對的機率。B、C、D 則同理
df.loc[df["true_answere"] == "A", "correct_rate"] = df["choose_a_population"]/df["test_population"]
df.loc[df["true_answere"] == "B", "correct_rate"] = df["choose_b_population"]/df["test_population"]
df.loc[df["true_answere"] == "C", "correct_rate"] = df["choose_c_population"]/df["test_population"]
df.loc[df["true_answere"] == "D", "correct_rate"] = df["choose_d_population"]/df["test_population"]
# 印出來看看
print(df)

# df 匯出 csv 
df.to_csv("arrange.csv", index=False)

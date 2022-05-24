from dataclasses import field
from site import abs_paths
import win32com.client as win32 
import pandas as pd 
import numpy as np 
from pathlib import Path 
import re 
import sys 
import os
# 參考影片:https://www.youtube.com/watch?v=ZS4d3JvbQHQ

def csv_to_excel(from_path, to_path, sheet_name):
    # 將 csv 轉換成 excel，表名為 Data
    df = pd.read_csv(
        # "arrange.csv",
        from_path,
        )
    # remove null values
    df = df.dropna()
    # write the csv file to xlsx File to create Pivot Table
    # df.to_excel("question_statistic_pivot_table.xlsx", sheet_name = 'Data', index = False)
    df.to_excel(to_path, sheet_name = sheet_name, index = False)

def clear_pts(ws):
    # 清乾淨 worksheet
    for pt in ws.PivotTables():
        pt.TableRange2.Clear()

def insert_pt_field_set1(pt):
    # 插入欄位名稱
    field_rows = {}
    field_rows["subject_table"] = pt.PivotFields("test_subject_table")
    field_rows["question_id"] = pt.PivotFields("question_id")

    # 建立值
    field_values = {}
    field_values["test_population"] = pt.PivotFields("test_population")
    field_values["choose_a_population"] = pt.PivotFields("choose_a_population")
    field_values["choose_b_population"] = pt.PivotFields("choose_b_population")
    field_values["choose_c_population"] = pt.PivotFields("choose_c_population")
    field_values["choose_d_population"] = pt.PivotFields("choose_d_population")
    field_values["correct_rate"] = pt.PivotFields("correct_rate")
    field_values["choose_a_probability"] = pt.PivotFields("choose_a_probability")
    field_values["choose_b_probability"] = pt.PivotFields("choose_b_probability")
    field_values["choose_c_probability"] = pt.PivotFields("choose_c_probability")
    field_values["choose_d_probability"] = pt.PivotFields("choose_d_probability")

    # insert row fields to pivot table designer
    # https://docs.microsoft.com/en-us/office/vba/api/excel.xlpivotfieldorientation
    field_rows["subject_table"].Orientation = 1 # xlRowField
    field_rows["subject_table"].Position = 1

    field_rows["question_id"].Orientation = 1
    # field_rows["question_id"].Position = 2

    # insert data field
    field_values["test_population"].Orientation = 4 # xlDataField
    field_values["test_population"].Function = -4157 # https://docs.microsoft.com/en-us/office/vba/api/excel.xlconsolidationfunction
    field_values["test_population"].NumberFormat = "#,##0" # https://support.microsoft.com/en-us/office/number-format-codes-5026bbd6-04bc-48cd-bf33-80f18b4eae68

    field_values["choose_a_population"].Orientation = 4 
    field_values["choose_a_population"].Function = -4157 
    field_values["choose_a_population"].NumberFormat = "#,##0" # Format for positive numbers

    field_values["choose_b_population"].Orientation = 4 
    field_values["choose_b_population"].Function = -4157 
    field_values["choose_b_population"].NumberFormat = "#,##0"

    field_values["choose_c_population"].Orientation = 4
    field_values["choose_c_population"].Function = -4157
    field_values["choose_c_population"].NumberFormat = "#,##0"

    field_values["choose_d_population"].Orientation = 4
    field_values["choose_d_population"].Function = -4157
    field_values["choose_d_population"].NumberFormat = "#,##0"

    field_values["correct_rate"].Orientation = 4
    field_values["correct_rate"].Function = -4106 # xlAverage
    field_values["correct_rate"].NumberFormat = "#,##0.00"

    field_values["choose_a_probability"].Orientation = 4
    field_values["choose_a_probability"].Function = -4106 
    field_values["choose_a_probability"].NumberFormat = "#,##0.00"

    field_values["choose_b_probability"].Orientation = 4
    field_values["choose_b_probability"].Function = -4106 
    field_values["choose_b_probability"].NumberFormat = "#,##0.00"

    field_values["choose_c_probability"].Orientation = 4
    field_values["choose_c_probability"].Function = -4106 
    field_values["choose_c_probability"].NumberFormat = "#,##0.00"

    field_values["choose_d_probability"].Orientation = 4
    field_values["choose_d_probability"].Function = -4106 
    field_values["choose_d_probability"].NumberFormat = "#,##0.00"
    

# 取出絕對路徑
abs_path = os.path.abspath("question_statistic_pivot_table.xlsx")
# print(abs_path)

xlApp = win32.Dispatch('Excel.Application')
xlApp.Visible = True

# 工作簿 workbook，放入 excel 路徑
wb = xlApp.Workbooks.Open(abs_path)
# 工作頁 worksheet
ws_data = wb.Worksheets("Data")
# print(ws_data.Name)

# # 創建一個 worksheet 叫做 report，若以建立 直接註解掉即可
# add = wb.Sheets.Add(Before = None , After = wb.Sheets(wb.Sheets.count))
# add.Name = "Report"

ws_report = wb.Worksheets("Report")

# 清理 pivot table，創建前先清乾淨
clear_pts(ws_report)

# 建立 pivot table 緩存連線
# https://docs.microsoft.com/zh-tw/office/vba/api/excel.xlpivottablesourcetype # xlDatabase => value = 1 
pt_cache = wb.PivotCaches().Create(1, ws_data.Range("A1").CurrentRegion)

# 創建 pivot table designer/editor
pt = pt_cache.CreatePivotTable(ws_report.Range("A1"), "MyReport_Summary")

# toggle grand totals
pt.ColumnGrand = True # 顯示 欄總計
pt.RowGrand = False # 顯示 列總計

# change subtotal location # 變更所有現有 PivotField 的小計位置
pt.SubtotalLocation(2) # 2 -> bottom; 1 -> top

# change report layout 
pt.RowAxisLayout(0)

# change pivot table style
pt.TableStyle2 = "PivotStyleMedium9"

# create report
insert_pt_field_set1(pt)

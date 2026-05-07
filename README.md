# 💉 疫苗接種記錄管理工具

本地運行的個人疫苗接種記錄 Dashboard，基於 Python + Streamlit 開發。

## 功能列表

- **Dashboard**：總覽統計、每年接種次數、左右臂比例
- **Records**：表格瀏覽、多條件篩選、關鍵字搜尋、直接編輯、刪除記錄
- **Add Record**：表單新增接種記錄，ID 自動遞增
- **Reports**：接種時間線、疫苗次數、接種單位、年度統計等圖表
- **Data Quality**：自動檢查重複 ID、日期格式、劑次格式、接種部位合法性
- **Export**：一鍵下載 CSV

## 安裝方式

```bash
pip install -r requirements.txt
```

## 運行方式

```bash
streamlit run app.py
```

瀏覽器會自動開啟 `http://localhost:8501`

## 資料檔說明

預設資料檔：`vaccine_records_cleaned.csv`（不存在時自動建立）

| 欄位 | 說明 |
|------|------|
| id | 序號（整數，自動遞增） |
| name | 疫苗名稱 |
| dose | 劑次（整數） |
| date | 接種日期（YYYY-MM-DD） |
| manufacturer | 生產企業 |
| batch | 批號 |
| arm | 接種部位（L / R / 空） |
| provider | 接種單位 |

> 程式會自動相容舊版欄位名稱（`vaccine_name`、`vaccination_date`、`batch_no`）

## 後續可改進功能

- 支援多人記錄（加入 person 欄位）
- 疫苗到期提醒 / 下次接種日期推算
- 匯入外部 CSV 功能
- 資料備份 / 版本歷史
- 行動裝置友好的 RWD 排版
- 匯出 PDF 接種證明

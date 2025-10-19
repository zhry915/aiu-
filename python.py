import os
import pandas as pd

# -----------------------------
# 1️⃣ CSV 文件所在文件夹
# -----------------------------
csv_folder = r"D:\stock_analysis_project\stock\stock data"
csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.lower().endswith('.csv')]
print(f"共找到 {len(csv_files)} 个 CSV 文件")

# -----------------------------
# 2️⃣ 读取本地股票列表
# -----------------------------
sz_file = r"D:\stock_analysis_project\A股列表.xlsx"
sh_file = r"D:\stock_analysis_project\GPLIST.xls"

sz_df = pd.read_excel(sz_file)
sh_df = pd.read_excel(sh_file)

# 只保留必要列
sz_df = sz_df[['A股代码', '公司全称', '所属行业']]
sh_df = sh_df[['A股代码', '公司英文全称']]

# -----------------------------
# 3️⃣ 生成股票代码到公司名称映射
# -----------------------------
code_to_name = dict(zip(sz_df['A股代码'].astype(str).str.lstrip('0'), sz_df['公司全称']))
code_to_name.update(dict(zip(sh_df['A股代码'].astype(str).str.lstrip('0'), sh_df['公司英文全称'])))

# -----------------------------
# 4️⃣ 读取 CSV 并合并
# -----------------------------
price_dfs = []

for file in csv_files:
    df = pd.read_csv(file)
    if 'trade_date' not in df.columns or 'close' not in df.columns:
        continue

    stock_code = os.path.basename(file).split('.')[0].lstrip('0')
    temp_df = df[['trade_date', 'close']].copy()

    # 映射为公司名称，如果找不到就保留股票代码
    stock_name = code_to_name.get(stock_code, stock_code)
    temp_df.rename(columns={'close': stock_name}, inplace=True)

    # 转换 trade_date 为 datetime，假设格式为 YYYYMMDD
    temp_df['trade_date'] = pd.to_datetime(temp_df['trade_date'].astype(str), format='%Y%m%d', errors='coerce')
    temp_df.dropna(subset=['trade_date'], inplace=True)
    temp_df.set_index('trade_date', inplace=True)
    price_dfs.append(temp_df)

if price_dfs:
    price_df = pd.concat(price_dfs, axis=1)
    price_df.sort_index(inplace=True)
    price_df.ffill(inplace=True)
    print("合并后数据预览:")
    print(price_df.head())
else:
    raise ValueError("没有找到可用的 CSV 文件。")

# -----------------------------
# 5️⃣ 自动生成板块字典（深交 & 上交）
# -----------------------------
sector_dict = {}

# SZ 板块，根据所属行业
for industry in sz_df['所属行业'].dropna().unique():
    sector_dict[industry] = sz_df[sz_df['所属行业'] == industry]['公司全称'].tolist()

# SH 股票统一放到 "上海股" 板块
sh_stocks = sh_df['公司英文全称'].tolist()
sector_dict['上海股'] = sh_stocks

# -----------------------------
# 6️⃣ 计算板块平均价
# -----------------------------
sector_avg = pd.DataFrame(index=price_df.index)
for sector, companies in sector_dict.items():
    valid_companies = [c for c in companies if c in price_df.columns]
    if valid_companies:
        sector_avg[sector] = price_df[valid_companies].mean(axis=1)
    print(f"{sector} 有效股票: {valid_companies}")

print("\n板块平均价预览:")
print(sector_avg.head())

# -----------------------------
# 7️⃣ 计算板块相关系数
# -----------------------------
if not sector_avg.empty:
    corr_matrix = sector_avg.corr()
    print("\n板块相关系数矩阵:")
    print(corr_matrix)
else:
    print("板块数据为空，无法计算相关系数")

# -----------------------------
# 8️⃣ 板块联动分析（指定板块 & 时间段）
# -----------------------------
start_date = "2023-01-01"
end_date = "2023-06-30"
target_sector = "C 制造业"  # 例：军工板块也可以写成 '军工'

# 筛选时间段数据
price_period = price_df[(price_df.index >= start_date) & (price_df.index <= end_date)]

# 板块内有效股票
sector_stocks = [c for c in sector_dict.get(target_sector, []) if c in price_period.columns]
if not sector_stocks:
    raise ValueError(f"{target_sector} 板块没有有效股票数据")

# 板块内股票价格
sector_prices = price_period[sector_stocks]

# 计算相关系数矩阵
corr_matrix = sector_prices.corr()
print(f"\n{target_sector} 板块股票相关系数矩阵:")
print(corr_matrix)

# 输出每只股票在板块内的相关性降序排名
for stock in sector_stocks:
    ranking = corr_matrix[stock].sort_values(ascending=False)
    print(f"\n以 {stock} 为基准的板块内相关性降序排名:")
    print(ranking)










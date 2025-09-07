import streamlit as st
import akshare as ak
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys

# --- Page Configuration ---
st.set_page_config(
    page_title="AKShare Macro Data Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Mapping & UI Structures ---
NBS_DATA_STRUCTURE = {
    "年度数据": {
        "国民经济核算": {"国内生产总值": None, "支出法国内生产总值": None, "国民总收入": None},
        "人口": {"总人口": None, "人口数及其构成": None, "人口的城乡构成": None},
        "就业和工资": {"就业基本情况": None, "城镇单位就业人员及工资": None},
        "价格": {"居民消费价格指数": None, "商品零售价格指数": None}
    },
    "季度数据": {
        "国民经济核算": {"国内生产总值": None, "三大产业贡献率": None},
        "农业": {"主要农产品产量": None}
    },
    "月度数据": {
        "价格": {"居民消费价格指数": None, "工业生产者价格指数": None},
        "工业": {"工业增加值": None, "主要工业产品产量": None},
        "固定资产投资": {"固定资产投资（不含农户）": None}
    }
}
NBS_REGION_DATA_STRUCTURE = {
    "分省年度数据": {"国民经济核算": {"地区生产总值": None}, "人民生活": {"居民消费水平": None}},
    "分省季度数据": {"国民经济核算": {"地区生产总值": None}, "人民生活": {"居民人均可支配收入": None}}
}

AKSHARE_MACRO_MAP = {
    "中国宏观": {
        "中国宏观杠杆率": {"func": ak.macro_cnbs, "desc": "中国国家金融与发展实验室-中国宏观杠杆率数据", "url": "http://114.115.232.154:8080/"},
        "企业商品价格指数": {"func": ak.macro_china_qyspjg, "desc": "东方财富-经济数据一览-中国-企业商品价格指数", "url": "http://data.eastmoney.com/cjsj/qyspjg.html"},
        "外商直接投资数据": {"func": ak.macro_china_fdi, "desc": "东方财富-经济数据一览-中国-外商直接投资数据", "url": "https://data.eastmoney.com/cjsj/fdi.html"},
        "LPR品种数据": {"func": ak.macro_china_lpr, "desc": "中国 LPR 品种数据", "url": "https://data.eastmoney.com/cjsj/globalRateLPR.html"},
        "城镇调查失业率": {"func": ak.macro_china_urban_unemployment, "desc": "国家统计局-月度数据-城镇调查失业率", "url": "https://data.stats.gov.cn/easyquery.htm?cn=A01&zb=A0203&sj=202304"},
        "社会融资规模增量统计": {"func": ak.macro_china_shrzgm, "desc": "商务数据中心-国内贸易-社会融资规模增量统计", "url": "http://data.mofcom.gov.cn/gnmy/shrzgm.shtml"},
        "中国 GDP 年率": {"func": ak.macro_china_gdp_yearly, "desc": "金十数据中心-中国 GDP 年率报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_gdp_yoy"},
        "中国 CPI 年率报告": {"func": ak.macro_china_cpi_yearly, "desc": "中国年度 CPI 数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_cpi_yoy"},
        "中国 CPI 月率报告": {"func": ak.macro_china_cpi_monthly, "desc": "中国月度 CPI 数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_cpi_mom"},
        "中国 PPI 年率报告": {"func": ak.macro_china_ppi_yearly, "desc": "中国年度 PPI 数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_ppi_yoy"},
        "以美元计算出口年率": {"func": ak.macro_china_exports_yoy, "desc": "中国以美元计算出口年率报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_exports_yoy"},
        "以美元计算进口年率": {"func": ak.macro_china_imports_yoy, "desc": "中国以美元计算进口年率报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_imports_yoy"},
        "以美元计算贸易帐": {"func": ak.macro_china_trade_balance, "desc": "中国以美元计算贸易帐报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_trade_balance"},
        "工业增加值增长": {"func": ak.macro_china_gyzjz, "desc": "东方财富-中国工业增加值增长", "url": "https://data.eastmoney.com/cjsj/gyzjz.html"},
        "规模以上工业增加值年率": {"func": ak.macro_china_industrial_production_yoy, "desc": "中国规模以上工业增加值年率报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_industrial_production_yoy"},
        "官方制造业 PMI": {"func": ak.macro_china_pmi_yearly, "desc": "中国年度PMI数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_manufacturing_pmi"},
        "财新制造业PMI终值": {"func": ak.macro_china_cx_pmi_yearly, "desc": "中国年度财新 PMI 数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_caixin_manufacturing_pmi"},
        "财新服务业PMI": {"func": ak.macro_china_cx_services_pmi_yearly, "desc": "中国财新服务业 PMI 报告", "url": "https://datacenter.jin10.com/reportType/dc_chinese_caixin_services_pmi"},
        "中国官方非制造业PMI": {"func": ak.macro_china_non_man_pmi, "desc": "中国官方非制造业 PMI", "url": "https://datacenter.jin10.com/reportType/dc_chinese_non_manufacturing_pmi"},
        "外汇储备": {"func": ak.macro_china_fx_reserves_yearly, "desc": "中国年度外汇储备数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_fx_reserves"},
        "M2货币供应年率": {"func": ak.macro_china_m2_yearly, "desc": "中国年度 M2 数据", "url": "https://datacenter.jin10.com/reportType/dc_chinese_m2_money_supply_yoy"},
        "新房价指数": {"func": ak.macro_china_new_house_price, "desc": "中国新房价指数月度数据", "url": "http://data.eastmoney.com/cjsj/newhouse.html", "params": ["city_first", "city_second"]},
        "企业景气及企业家信心指数": {"func": ak.macro_china_enterprise_boom_index, "desc": "中国企业景气及企业家信心指数数据", "url": "http://data.eastmoney.com/cjsj/qyjqzs.html"},
        "全国税收收入": {"func": ak.macro_china_national_tax_receipts, "desc": "中国全国税收收入数据", "url": "http://data.eastmoney.com/cjsj/nationaltaxreceipts.aspx"},
        "银行理财产品发行数量": {"func": ak.macro_china_bank_financing, "desc": "银行理财产品发行数量", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI01516267.html"},
        "原保险保费收入": {"func": ak.macro_china_insurance_income, "desc": "原保险保费收入", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMM00088870.html"},
        "手机出货量": {"func": ak.macro_china_mobile_number, "desc": "手机出货量", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00225823.html"},
        "菜篮子产品批发价格指数": {"func": ak.macro_china_vegetable_basket, "desc": "菜篮子产品批发价格指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00009275.html"},
        "农产品批发价格总指数": {"func": ak.macro_china_agricultural_product, "desc": "农产品批发价格总指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00009274.html"},
        "农副指数": {"func": ak.macro_china_agricultural_index, "desc": "农副指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00662543.html"},
        "能源指数": {"func": ak.macro_china_energy_index, "desc": "能源指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00662539.html"},
        "大宗商品价格指数": {"func": ak.macro_china_commodity_price_index, "desc": "大宗商品价格数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00662535.html"},
        "费城半导体指数": {"func": ak.macro_global_sox_index, "desc": "费城半导体指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00055562.html"},
        "义乌小商品指数-电子元器件": {"func": ak.macro_china_yw_electronic_index, "desc": "义乌小商品指数-电子元器件数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00055551.html"},
        "建材指数": {"func": ak.macro_china_construction_index, "desc": "建材指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00662541.html"},
        "建材价格指数": {"func": ak.macro_china_construction_price_index, "desc": "建材价格指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00237146.html"},
        "物流景气指数": {"func": ak.macro_china_lpi_index, "desc": "物流景气指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00352262.html"},
        "原油运输指数": {"func": ak.macro_china_bdti_index, "desc": "原油运输指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107668.html"},
        "超灵便型船运价指数": {"func": ak.macro_china_bsi_index, "desc": "超灵便型船运价指数数据", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107667.html"},
        "海岬型运费指数": {"func": ak.macro_shipping_bci, "desc": "海岬型运费指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107666.html"},
        "波罗的海干散货指数": {"func": ak.macro_shipping_bdi, "desc": "波罗的海干散货指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107664.html"},
        "巴拿马型运费指数": {"func": ak.macro_shipping_bpi, "desc": "巴拿马型运费指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107665.html"},
        "成品油运输指数": {"func": ak.macro_shipping_bcti, "desc": "成品油运输指数", "url": "https://data.eastmoney.com/cjsj/hyzs_list_EMI00107669.html"},
        "新增信贷数据": {"func": ak.macro_china_new_financial_credit, "desc": "中国新增信贷数据数据", "url": "http://data.eastmoney.com/cjsj/xzxd.html"},
        "居民消费价格指数": {"func": ak.macro_china_cpi, "desc": "中国居民消费价格指数", "url": "http://data.eastmoney.com/cjsj/cpi.html"},
        "国内生产总值": {"func": ak.macro_china_gdp, "desc": "中国国内生产总值", "url": "http://data.eastmoney.com/cjsj/gdp.html"},
        "工业品出厂价格指数": {"func": ak.macro_china_ppi, "desc": "工业品出厂价格指数", "url": "http://data.eastmoney.com/cjsj/ppi.html"},
        "采购经理人指数": {"func": ak.macro_china_pmi, "desc": "采购经理人指数", "url": "http://data.eastmoney.com/cjsj/pmi.html"},
        "中国城镇固定资产投资": {"func": ak.macro_china_gdzctz, "desc": "中国城镇固定资产投资", "url": "http://data.eastmoney.com/cjsj/gdzctz.html"},
        "海关进出口增减情况": {"func": ak.macro_china_hgjck, "desc": "中国海关进出口增减情况一览表", "url": "https://data.eastmoney.com/cjsj/hgjck.html"},
        "财政收入": {"func": ak.macro_china_czsr, "desc": "中国财政收入", "url": "http://data.eastmoney.com/cjsj/czsr.html"},
        "外汇贷款数据": {"func": ak.macro_china_whxd, "desc": "外汇贷款数据", "url": "http://data.eastmoney.com/cjsj/whxd.html"},
        "本外币存款": {"func": ak.macro_china_wbck, "desc": "本外币存款", "url": "http://data.eastmoney.com/cjsj/wbck.html"},
        "新债发行": {"func": ak.macro_china_bond_public, "desc": "中国外汇交易中心暨全国银行间同业拆借中心-债券信息披露-新债发行", "url": "https://www.chinamoney.com.cn/chinese/xzjfx/"},
        "消费者信心指数": {"func": ak.macro_china_xfzxx, "desc": "东方财富网-消费者信心指数", "url": "https://data.eastmoney.com/cjsj/xfzxx.html"},
        "存款准备金率": {"func": ak.macro_china_reserve_requirement_ratio, "desc": "国家统计局-存款准备金率", "url": "https://data.eastmoney.com/cjsj/ckzbj.html"},
        "社会消费品零售总额": {"func": ak.macro_china_consumer_goods_retail, "desc": "东方财富-经济数据-社会消费品零售总额", "url": "http://data.eastmoney.com/cjsj/xfp.html"},
        "全社会用电分类情况表": {"func": ak.macro_china_society_electricity, "desc": "国家统计局-全社会用电分类情况表", "url": "http://finance.sina.com.cn/mac/#industry-6-0-31-1"},
        "全社会客货运输量": {"func": ak.macro_china_society_traffic_volume, "desc": "国家统计局-全社会客货运输量-非累计", "url": "http://finance.sina.com.cn/mac/#industry-10-0-31-1"},
        "邮电业务基本情况": {"func": ak.macro_china_postal_telecommunicational, "desc": "国家统计局-邮电业务基本情况-非累计", "url": "http://finance.sina.com.cn/mac/#industry-11-0-31-1"},
        "国际旅游外汇收入构成": {"func": ak.macro_china_international_tourism_fx, "desc": "国家统计局-国际旅游外汇收入构成", "url": "http://finance.sina.com.cn/mac/#industry-15-0-31-3"},
        "民航客座率及载运率": {"func": ak.macro_china_passenger_load_factor, "desc": "国家统计局-民航客座率及载运率", "url": "http://finance.sina.com.cn/mac/#industry-20-0-31-1"},
        "航贸运价指数": {"func": ak.macro_china_freight_index, "desc": "新浪财经-中国宏观经济数据-航贸运价指数", "url": "http://finance.sina.com.cn/mac/#industry-22-0-31-2"},
        "央行货币当局资产负债": {"func": ak.macro_china_central_bank_balance, "desc": "新浪财经-中国宏观经济数据-央行货币当局资产负债", "url": "http://finance.sina.com.cn/mac/#fininfo-8-0-31-2"},
        "保险业经营情况": {"func": ak.macro_china_insurance, "desc": "新浪财经-中国宏观经济数据-保险业经营情况", "url": "http://finance.sina.com.cn/mac/#fininfo-19-0-31-3"},
        "货币供应量": {"func": ak.macro_china_supply_of_money, "desc": "新浪财经-中国宏观经济数据-货币供应量", "url": "http://finance.sina.com.cn/mac/#fininfo-1-0-31-1"},
        "FR007利率互换曲线历史数据": {"func": ak.macro_china_swap_rate, "desc": "国家统计局-FR007利率互换曲线历史数据 (近一年)", "url": "https://www.chinamoney.com.cn/chinese/bkcurvfxhis/?cfgItemType=72&curveType=FR007", "params": ["start_date", "end_date"]},
        "央行黄金和外汇储备": {"func": ak.macro_china_foreign_exchange_gold, "desc": "国家统计局-央行黄金和外汇储备", "url": "http://finance.sina.com.cn/mac/#fininfo-5-0-31-2"},
        "商品零售价格指数": {"func": ak.macro_china_retail_price_index, "desc": "国家统计局-商品零售价格指数", "url": "http://finance.sina.com.cn/mac/#price-12-0-31-1"},
        "国房景气指数": {"func": ak.macro_china_real_estate, "desc": "国家统计局-国房景气指数", "url": "http://data.eastmoney.com/cjsj/hyzs_list_EMM00121987.html"},
        "外汇和黄金储备": {"func": ak.macro_china_fx_gold, "desc": "中国外汇和黄金储备", "url": "http://data.eastmoney.com/cjsj/hjwh.html"},
        "中国货币供应量": {"func": ak.macro_china_money_supply, "desc": "东方财富-经济数据-中国宏观-中国货币供应量", "url": "http://data.eastmoney.com/cjsj/hbgyl.html"},
        "全国股票交易统计表": {"func": ak.macro_china_stock_market_cap, "desc": "全国股票交易统计表", "url": "http://data.eastmoney.com/cjsj/gpjytj.html"},
        "上海银行业同业拆借报告": {"func": ak.macro_china_shibor_all, "desc": "上海银行业同业拆借报告", "url": "https://datacenter.jin10.com/reportType/dc_shibor"},
        "人民币香港银行同业拆息": {"func": ak.macro_china_hk_market_info, "desc": "香港同业拆借报告", "url": "https://datacenter.jin10.com/reportType/dc_hk_market_info"},
        "中国日度沿海六大电库存(历史)": {"func": ak.macro_china_daily_energy, "desc": "中国日度沿海六大电库存数据(不再更新)", "url": "https://datacenter.jin10.com/reportType/dc_qihuo_energy_report"},
        "人民币汇率中间价报告(历史)": {"func": ak.macro_china_rmb, "desc": "中国人民币汇率中间价报告(2017-2021)", "url": "https://datacenter.jin10.com/reportType/dc_rmb_data"},
        "深圳融资融券报告": {"func": ak.macro_china_market_margin_sz, "desc": "深圳融资融券报告", "url": "https://datacenter.jin10.com/reportType/dc_market_margin_sz"},
        "上海融资融券报告": {"func": ak.macro_china_market_margin_sh, "desc": "上海融资融券报告", "url": "https://datacenter.jin10.com/reportType/dc_market_margin_sse"},
        "上海黄金交易所报告": {"func": ak.macro_china_au_report, "desc": "上海黄金交易所报告", "url": "https://datacenter.jin10.com/reportType/dc_sge_report"},
        "股票筹资": {"func": ak.macro_stock_finance, "desc": "同花顺-数据中心-宏观数据-股票筹资", "url": "https://data.10jqka.com.cn/macro/finance/"},
        "新增人民币贷款": {"func": ak.macro_rmb_loan, "desc": "同花顺-数据中心-宏观数据-新增人民币贷款", "url": "https://data.10jqka.com.cn/macro/loan/"},
        "人民币存款余额": {"func": ak.macro_rmb_deposit, "desc": "同花顺-数据中心-宏观数据-人民币存款余额", "url": "https://data.10jqka.com.cn/macro/rmb/"},
    },
    "国家统计局(通用接口)": {
        "全国数据": {"func": ak.macro_china_nbs_nation, "desc": "国家统计局全国数据通用接口。请通过下面的下拉菜单选择数据路径。", "url": "https://data.stats.gov.cn/easyquery.htm", "params": ["ui_nbs_nation"]},
        "地区数据": {"func": ak.macro_china_nbs_region, "desc": "国家统计局地区数据通用接口。请通过下面的下拉菜单选择数据路径。", "url": "https://data.stats.gov.cn/easyquery.htm", "params": ["ui_nbs_region"]},
    },
    "全球宏观": {
        "宏观日历-华尔街见闻": {"func": ak.macro_info_ws, "desc": "华尔街见闻-日历-宏观", "url": "https://wallstreetcn.com/calendar", "params": ["date"]},
        "全球宏观事件-百度": {"func": ak.news_economic_baidu, "desc": "全球宏观指标重大事件", "url": "https://gushitong.baidu.com/calendar", "params": ["date"]},
    },
    "重要机构": {
       "SPDR黄金ETF持仓": {"func": ak.macro_cons_gold, "desc": "全球最大黄金 ETF—SPDR Gold Trust 持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_etf_gold"},
       "iShares白银ETF持仓": {"func": ak.macro_cons_silver, "desc": "全球最大白银 ETF--iShares Silver Trust 持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_etf_sliver"},
       "欧佩克月度报告": {"func": ak.macro_cons_opec_month, "desc": "欧佩克月度原油产量报告", "url": "https://datacenter.jin10.com/reportType/dc_opec_report"},
       "LME持仓报告": {"func": ak.macro_euro_lme_holding, "desc": "伦敦金属交易所(LME)-持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_lme_traders_report"},
       "LME库存报告": {"func": ak.macro_euro_lme_stock, "desc": "伦敦金属交易所(LME)-库存报告", "url": "https://datacenter.jin10.com/reportType/dc_lme_report"},
       "CFTC外汇类非商业持仓": {"func": ak.macro_usa_cftc_nc_holding, "desc": "美国商品期货交易委员会CFTC外汇类非商业持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_cftc_nc_report"},
       "CFTC商品类非商业持仓": {"func": ak.macro_usa_cftc_c_holding, "desc": "美国商品期货交易委员会CFTC商品类非商业持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_cftc_c_report"},
       "CFTC外汇类商业持仓": {"func": ak.macro_usa_cftc_merchant_currency_holding, "desc": "美国商品期货交易委员会CFTC外汇类商业持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_cftc_merchant_currency"},
       "CFTC商品类商业持仓": {"func": ak.macro_usa_cftc_merchant_goods_holding, "desc": "美国商品期货交易委员会 CFTC 商品类商业持仓报告", "url": "https://datacenter.jin10.com/reportType/dc_cftc_merchant_goods"},
       "CME贵金属成交量": {"func": ak.macro_usa_cme_merchant_goods_holding, "desc": "芝加哥交易所-贵金属成交量数据", "url": "https://datacenter.jin10.com/org"},
    },
    # Other countries...
}


@st.cache_data
def fetch_data(region_name, dataset_name, **kwargs):
    """
    Fetches data using a hashable dataset name and its region to ensure a unique cache key.
    """
    try:
        # This is the corrected logic: always look up the function from the map.
        func = AKSHARE_MACRO_MAP[region_name][dataset_name]["func"]
        data = func(**kwargs)
        return data
    except Exception as e:
        st.error(f"获取数据时发生错误: {e}")
        return None

def find_and_format_date_column(df):
    date_col_names = ['date', '日期', '年份', '月份', '季度', '时间', '统计时间', '数据日期', 'TRADE_DATE']
    df_copy = df.copy()
    if 'item' in df_copy.columns and 'value' in df_copy.columns and 'date' in df_copy.columns:
        try:
            df_copy['date'] = pd.to_datetime(df_copy['date'], format='%Y%m')
            df_pivot = df_copy.pivot(index='date', columns='item', values='value').reset_index()
            return df_pivot, 'date'
        except Exception:
            pass
    for col in df_copy.columns:
        if any(name in col.lower() for name in date_col_names):
            try:
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                df_copy.dropna(subset=[col], inplace=True)
                return df_copy, col
            except Exception:
                continue
    return df_copy, None

def render_nbs_ui(dataset_name):
    st.sidebar.subheader("数据路径选择")
    param_inputs = {}
    data_structure = NBS_DATA_STRUCTURE if dataset_name == "全国数据" else NBS_REGION_DATA_STRUCTURE
    
    kind = st.sidebar.selectbox("选择数据类型", list(data_structure.keys()), key=f"nbs_{dataset_name}_kind")
    param_inputs['kind'] = kind
    
    level1_keys = list(data_structure[kind].keys())
    level1_choice = st.sidebar.selectbox("选择一级目录", level1_keys, key=f"nbs_{dataset_name}_l1")
    path_parts = [level1_choice]
    
    level2_data = data_structure[kind].get(level1_choice)
    if isinstance(level2_data, dict):
        level2_keys = list(level2_data.keys())
        level2_choice = st.sidebar.selectbox("选择二级目录", level2_keys, key=f"nbs_{dataset_name}_l2")
        path_parts.append(level2_choice)
    
    param_inputs['path'] = " > ".join(path_parts)
    st.sidebar.success(f"已选路径: `{param_inputs['path']}`")

    if dataset_name == "地区数据":
        param_inputs['indicator'] = st.sidebar.text_input("输入指标 (indicator)", "例如: 地区生产总值_累计值(亿元)")
        param_inputs['region'] = st.sidebar.text_input("输入地区 (region)", "例如: 河北省")

    st.sidebar.subheader("时间区间")
    st.sidebar.markdown("示例: `2023` (年), `2023A` (季), `LAST10` (最近10期)")
    param_inputs['period'] = st.sidebar.text_input("输入 period", "LAST10")
    
    return param_inputs

def main():
    st.title("📈 AKShare 宏观数据可视化平台")
    st.markdown("从侧边栏选择一个宏观经济数据集进行探索。")

    if 'data' not in st.session_state:
        st.session_state.data = None
        st.session_state.dataset_name = ""
        st.session_state.dataset_info = {}

    st.sidebar.header("数据选择")
    
    selected_region = st.sidebar.selectbox(
        "选择一个国家/地区:",
        list(AKSHARE_MACRO_MAP.keys()),
        on_change=lambda: st.session_state.clear()
    )

    region_datasets = AKSHARE_MACRO_MAP[selected_region]
    selected_dataset_name = st.sidebar.selectbox(
        "选择一个数据集:",
        list(region_datasets.keys()),
        on_change=lambda: st.session_state.clear()
    )
    
    dataset_info = region_datasets[selected_dataset_name]
    params = dataset_info.get("params", [])
    
    desc = dataset_info['desc']
    url = dataset_info.get('url', 'N/A')
    st.sidebar.info(f"**数据描述:**\n\n{desc}\n\n**数据源地址:**\n\n{url}")

    param_inputs = {}
    is_nbs_interface = "ui_nbs" in params[0] if params else False
    
    if is_nbs_interface:
        param_inputs = render_nbs_ui(selected_dataset_name)
    elif params:
        st.sidebar.subheader("接口参数")
        for p in params:
            if "date" in p:
                today = datetime.today()
                val = st.sidebar.date_input(f"输入 {p}", value=today if p != "start_date" else pd.to_datetime("2024-01-01"))
                param_inputs[p] = val.strftime("%Y%m%d")
            elif "city" in p:
                param_inputs[p] = st.sidebar.text_input(f"输入 {p}", value="北京" if p == "city_first" else "上海")
    
    if st.sidebar.button("获取并可视化数据", type="primary"):
        with st.spinner("正在加载数据..."):
            # The simplified and corrected call. No more 'func_obj'.
            df_raw = fetch_data(selected_region, selected_dataset_name, **param_inputs)
            st.session_state.data = df_raw
            st.session_state.dataset_name = selected_dataset_name
            st.session_state.dataset_info = dataset_info
    
    if st.session_state.data is not None:
        df_raw = st.session_state.data
        
        if isinstance(df_raw, pd.DataFrame) and not df_raw.empty:
            st.header(f"📊 {st.session_state.dataset_name}")
            info = st.session_state.dataset_info
            st.markdown(f"**数据描述:** {info['desc']}")
            st.markdown(f"**数据源地址:** [{info.get('url', 'N/A')}]({info.get('url', 'N/A')})")
            
            df, date_col = find_and_format_date_column(df_raw)
            
            st.subheader("数据预览 (原始文本保留)")
            st.dataframe(df)

            st.subheader("数据可视化")
            
            df_for_plotting = df.copy()
            if date_col:
                for col in df_for_plotting.columns:
                    if col != date_col:
                        df_for_plotting[col] = pd.to_numeric(df_for_plotting[col], errors='coerce')
                
                numeric_cols = df_for_plotting.select_dtypes(include=['number']).columns.tolist()
                
                if not numeric_cols:
                    st.warning("在数据中未找到可绘制的数值列。")
                else:
                    if date_col in numeric_cols:
                        numeric_cols.remove(date_col)
                    
                    if not numeric_cols:
                         st.warning("在数据中除日期外未找到可绘制的数值列。")
                    else:
                        y_axis_options = st.multiselect(
                            "选择要绘制的 Y 轴数据:",
                            options=numeric_cols,
                            default=numeric_cols[0] if numeric_cols else []
                        )

                        if y_axis_options:
                            try:
                                fig = px.line(
                                    df_for_plotting,
                                    x=date_col,
                                    y=y_axis_options,
                                    title=f"{st.session_state.dataset_name} - 时间序列图"
                                )
                                fig.update_traces(connectgaps=False)
                                fig.update_layout(xaxis_title="日期", yaxis_title="数值", legend_title_text='指标')
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"创建图表时出错: {e}. 请检查数据格式。")
                        else:
                            st.info("请至少选择一个 Y 轴数据进行绘图。")
            else:
                st.info("无法自动识别此数据集中的日期列用于绘制时间序列图。")
                
        elif isinstance(df_raw, str):
            st.error(f"获取数据失败: {df_raw}")
        else:
            st.warning("未能获取到数据。这可能是因为当前参数下没有可用数据，或者之前选择的数据已被清除。请重新点击“获取数据”按钮。")

if __name__ == "__main__":
    main()

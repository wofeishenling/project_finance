from PIL import Image
import io
import akshare as ak
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import warnings
import seaborn as sns
import base64
matplotlib.use('Agg')
def generate_images(input_string):
    # 处理input_string并生成四张图片
    # ...
    stockCode = input_string
    balancSheet_df = ak.stock_balance_sheet_by_yearly_em(symbol=stockCode)
    incomeStatement_df = ak.stock_profit_sheet_by_yearly_em(symbol=stockCode)
    cashFlowSheet_df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=stockCode)

    balancSheet_df = balancSheet_df.fillna(0)
    incomeStatement_df = incomeStatement_df.fillna(0)
    cashFlowSheet_df = cashFlowSheet_df.fillna(0)
    balancSheet_df['REPORT_DATE_NAME'] = balancSheet_df['REPORT_DATE_NAME'].str[:4]
    incomeStatement_df['REPORT_DATE_NAME'] = incomeStatement_df['REPORT_DATE_NAME'].str[:4]
    cashFlowSheet_df['REPORT_DATE_NAME'] = cashFlowSheet_df['REPORT_DATE_NAME'].str[:4]

    incomeStatement_df['GPM'] = (incomeStatement_df['OPERATE_INCOME'] - incomeStatement_df['OPERATE_COST'])/incomeStatement_df['OPERATE_INCOME']
    incomeStatement_df['coreIncome'] = incomeStatement_df['OPERATE_INCOME'] - incomeStatement_df['OPERATE_COST']\
                     - incomeStatement_df['OPERATE_TAX_ADD'] - incomeStatement_df['RESEARCH_EXPENSE']\
                     - incomeStatement_df['MANAGE_EXPENSE'] - incomeStatement_df['SALE_EXPENSE']\
                     - incomeStatement_df['FE_INTEREST_INCOME']

    incomeStatement_df['coreGPM'] = incomeStatement_df['coreIncome']/incomeStatement_df['OPERATE_INCOME']
    incomeStatement_df['investmentIncome'] = incomeStatement_df['FE_INTEREST_INCOME'] + incomeStatement_df['INVEST_INCOME'] + incomeStatement_df['FAIRVALUE_CHANGE_INCOME']
    incomeStatement_df['twoLoss'] = incomeStatement_df['CREDIT_IMPAIRMENT_INCOME'] + incomeStatement_df['ASSET_IMPAIRMENT_INCOME']
    coreIncomeRate_df = incomeStatement_df[['REPORT_DATE_NAME', 'coreIncome','investmentIncome','OTHER_INCOME','twoLoss']]
    operateAndRate_df = incomeStatement_df[['REPORT_DATE_NAME', 'OPERATE_INCOME','GPM','coreGPM']]
    stock_individual_info_em_df = ak.stock_individual_info_em(symbol=stockCode[2:])
    stockName = stock_individual_info_em_df['value'][5]
    sns.color_palette("rocket")
    plt.style.use('seaborn')
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
    zhfont = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/SimHei.ttf')
    plt.rcParams['axes.unicode_minus'] = False

    operateAndRate_df = operateAndRate_df.sort_values('REPORT_DATE_NAME')
    operateIncome_df = operateAndRate_df['OPERATE_INCOME']
    GPM_df = operateAndRate_df['GPM']
    coreGPM_df = operateAndRate_df['coreGPM']

    years = operateAndRate_df['REPORT_DATE_NAME']
    operate_income = operateAndRate_df['OPERATE_INCOME']

    fig, ax1 = plt.subplots(dpi=250, figsize=(16, 9))
    # 绘制柱状图
    ax1.bar(years, operate_income)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Operate Income')

    # 绘制折线图
    ax2 = ax1.twinx()

    # 绘制折线图
    ax2.plot(years, GPM_df, marker='o', linestyle='-', label='GPM', color = 'red')
    ax2.plot(years, coreGPM_df, marker='o', linestyle='-', label='Core GPM', color = 'pink')
    ax2.set_ylabel('GPM and coreGPM')

    # 添加图例
    ax2.legend()


    plt.legend()
    plt.title(stockName, fontproperties=zhfont)
    plt.savefig(stockName + '营收.png')

    sns.color_palette("rocket")
    plt.style.use('seaborn')
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
    zhfont = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/SimHei.ttf')
    plt.rcParams['axes.unicode_minus'] = False

    coreIncomeRate_df = coreIncomeRate_df.sort_values('REPORT_DATE_NAME')
    core_income = coreIncomeRate_df['coreIncome']
    investment_income = coreIncomeRate_df['investmentIncome']
    other_income = coreIncomeRate_df['OTHER_INCOME']
    two_loss = coreIncomeRate_df['twoLoss']

    plt.figure(dpi=250, figsize=(16, 9))

    positive_core_income = np.where(core_income>0, core_income, 0)
    negative_core_income = np.where(core_income<0, core_income, 0)

    positive_investment_income = np.where(investment_income>0, investment_income, 0)
    negative_investment_income = np.where(investment_income<0, investment_income, 0)

    positive_other_income = np.where(other_income>0, other_income, 0)
    negative_other_income = np.where(other_income<0, other_income, 0)

    positive_two_loss = np.where(two_loss>0, two_loss, 0)
    negative_two_loss = np.where(two_loss<0, two_loss, 0)
    # 创建柱状图
    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], positive_core_income, label='Positive Core Income')
    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], negative_core_income, label='Negative Core Income')

    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], positive_investment_income, bottom=positive_core_income, label='Positive Investment Income')
    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], negative_investment_income, bottom=negative_core_income, label='Negative Investment Income')

    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], positive_other_income, bottom=positive_core_income+positive_investment_income, label='Positive Other Income')
    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], negative_other_income, bottom=negative_core_income+negative_investment_income, label='Negative Other Income')

    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], positive_two_loss, bottom=positive_core_income+positive_investment_income+positive_other_income, label='Positive Impairment Loss')
    plt.bar(coreIncomeRate_df['REPORT_DATE_NAME'], negative_two_loss, bottom=negative_core_income+negative_investment_income+negative_other_income, label='Negative Impairment Loss')

    plt.legend()
    plt.title(stockName, fontproperties=zhfont)
    plt.savefig(stockName + '.png')

    coreIncome_df = incomeStatement_df[['REPORT_DATE_NAME', 'coreIncome']]
    netCashOperate_df = cashFlowSheet_df[['REPORT_DATE_NAME','NETCASH_OPERATE']]
    merged_df = coreIncome_df.merge(netCashOperate_df, on='REPORT_DATE_NAME')

    merged_df['CoreProfitRealizationRate'] = merged_df['NETCASH_OPERATE']/merged_df['coreIncome']
    sns.color_palette("rocket")
    plt.style.use('seaborn')
    merged_df = merged_df.sort_values('REPORT_DATE_NAME')
    # 数据
    report_date_name = merged_df['REPORT_DATE_NAME']
    core_profit_realization_rate = merged_df['CoreProfitRealizationRate']

    # 绘制折线图
    plt.figure(dpi=250, figsize=(16, 9))
    plt.plot(report_date_name, core_profit_realization_rate, marker='o')

    # 标注具体数值
    for i in range(len(report_date_name)):
        plt.annotate(f'{core_profit_realization_rate[i]:.2f}', (report_date_name[i], core_profit_realization_rate[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.axhline(1, color='gray', linestyle='dashed')
    # 设置标题和坐标轴标签
    plt.title("Core Profit Realization Rate Over Time", fontsize=16)
    plt.xlabel("Report Date Name", fontsize=12)
    plt.ylabel("Core Profit Realization Rate", fontsize=12)

    plt.savefig(stockName + '获现率.png')

    # 流动资金及负债
    balancSheet_df['WorkingCapital_Liabilitie'] = balancSheet_df['NOTE_ACCOUNTS_RECE'] + balancSheet_df['FINANCE_RECE'] + balancSheet_df['PREPAYMENT'] + \
                            balancSheet_df['TOTAL_OTHER_RECE'] + balancSheet_df['INVENTORY'] + balancSheet_df['CONTRACT_ASSET']\
                            - balancSheet_df['NOTE_ACCOUNTS_PAYABLE'] - balancSheet_df['ADVANCE_RECEIVABLES'] - balancSheet_df['CONTRACT_LIAB']\
                            - balancSheet_df['STAFF_SALARY_PAYABLE'] - balancSheet_df['TAX_PAYABLE'] - balancSheet_df['TOTAL_OTHER_PAYABLE']\
                            - balancSheet_df['PREDICT_LIAB']
    # 物业仓房机器等
    balancSheet_df['ProductiveAssets'] = balancSheet_df['FIXED_ASSET'] + balancSheet_df['CIP'] + balancSheet_df['USERIGHT_ASSET']
    # 无形资产
    # ???
    # 净现金+短期可以变现的资产
    balancSheet_df['ShortTermRealizableAssets'] = balancSheet_df['MONETARYFUNDS'] + balancSheet_df['TRADE_FINASSET_NOTFVTPL'] + balancSheet_df['OTHER_CURRENT_ASSET']
    # 需要时间变现的投资性资产
    balancSheet_df['InvestmentAssets'] = balancSheet_df['FVTPL_FINASSET'] + balancSheet_df['AVAILABLE_SALE_FINASSET'] + balancSheet_df['OTHER_EQUITY_INVEST']
    # 对子公司和相关公司的投资
    balancSheet_df['StrategicInvestments'] = balancSheet_df['LONG_EQUITY_INVEST']
    # 对其他非营运资产及债务
    # ???

    AssetStructure_df = balancSheet_df[['REPORT_DATE_NAME','WorkingCapital_Liabilitie','ProductiveAssets','ShortTermRealizableAssets','InvestmentAssets','StrategicInvestments']]
    AssetStructure_df = AssetStructure_df.sort_values('REPORT_DATE_NAME')
    AssetStructure_df['OperatingAssets'] = AssetStructure_df['WorkingCapital_Liabilitie'] + AssetStructure_df['ProductiveAssets']
    AssetStructure_df['NonWorkingCapital'] = AssetStructure_df['ShortTermRealizableAssets'] + AssetStructure_df['InvestmentAssets'] + AssetStructure_df['StrategicInvestments']
    AssetStructure_df.set_index('REPORT_DATE_NAME', inplace=True)
    merged_df.set_index('REPORT_DATE_NAME', inplace=True)

    year = '2022'
    # 营运资产
    OperatingAssets = round(AssetStructure_df.loc[year]['OperatingAssets']/1e9, 2)
    # 非营运资产（净值）
    NonOperatingAssets = round(AssetStructure_df.loc[year]['NonWorkingCapital']/1e9, 2)
    # WACC
    WACC = 0.1
    # EPV = [coreProfit*(1-taxRate)]/WACC
    taxRate = 0.14
    coreProfit = round((1-taxRate)*merged_df.loc['2022']['coreIncome']/1e9, 2)
    EPV = round(coreProfit/(WACC), 2)
    # Growth value
    g = 0.02 # 加权折合永续增长率 = 短期增长率与长期增长率的加权等效
    Gvalue = round(coreProfit/((WACC-g))-coreProfit/(WACC), 2)
    # 安全边际 discount
    discount = 0.8

    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
    zhfont = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/SimHei.ttf')
    plt.rcParams['axes.unicode_minus'] = False


    plt.figure(dpi=250, figsize=(16, 9))
    width = 0.6
    # 获取调色板
    sns.color_palette("rocket")
    plt.style.use('seaborn')
    # 数据
    label1 = ['Assets']
    label2 = ['EarningPower']
    label3 = ['GrowthValue']

    Mvalue = round((NonOperatingAssets+EPV+Gvalue)*discount, 2)
    IntangibleValue = round(Mvalue-NonOperatingAssets-OperatingAssets, 2)
    # 创建柱状图
    bar1 = plt.bar(label1, NonOperatingAssets, label='Non-Operating Assets',width=width)
    plt.bar(label1, OperatingAssets, bottom=NonOperatingAssets, label='Operating Assets',width=width)
    plt.bar(label1, Mvalue-(NonOperatingAssets+OperatingAssets), bottom=NonOperatingAssets+OperatingAssets, label='Operating Assets',width=width,alpha=0.5)

    bar2 = plt.bar(label2, EPV, bottom=NonOperatingAssets, label='Operating Assets',width=width)

    plt.bar(label3, Gvalue, bottom=EPV+NonOperatingAssets, label='Operating Assets',width=width)

    plt.text(label1[0], NonOperatingAssets/2, 'NonOperating:'+str(NonOperatingAssets), ha='center', va='center', color='white', fontsize=11)
    plt.text(label1[0], NonOperatingAssets + (OperatingAssets/2), 'OperatingAssets:'+str(OperatingAssets), ha='center', va='center', color='white', fontsize=11)
    plt.text(label1[0], (NonOperatingAssets+OperatingAssets+Mvalue)/2, 'IntangibleValue:'+str(IntangibleValue), ha='center', va='center', color='white', fontsize=10)
    plt.text(label2[0], (NonOperatingAssets*2+EPV)/2, 'EaringPower:'+str(EPV), ha='center', va='center', color='black', fontsize=11)
    plt.text(label2[0], NonOperatingAssets + (OperatingAssets/2), 'coreProfit:('+str(coreProfit)+')', ha='center', va='center', color='black', fontsize=11)
    plt.text(label1[0], (Mvalue+Mvalue/discount)/2, 'Security Boundary', ha='center', va='center', color='green', fontsize=13)
    plt.text(label3[0], NonOperatingAssets+EPV + (Gvalue/2), 'GrowthValue:'+str(Gvalue), ha='center', va='center', color='black', fontsize=11)
    plt.text(label1[0], Mvalue, 'MarketValuation:'+str(Mvalue), ha='center', va='bottom', color='red', fontsize=12)
    plt.axhline(NonOperatingAssets, color='gray', linestyle='dashed', xmin=0.05, xmax=0.6)
    plt.axhline(NonOperatingAssets + OperatingAssets, color='gray', linestyle='dashed', xmin=0.05, xmax=0.6)
    plt.axhline(NonOperatingAssets + EPV, color='gray', linestyle='dashed', xmin=0.4, xmax=1)
    plt.axhline(NonOperatingAssets + EPV + Gvalue, color='gray', linestyle='dashed')
    plt.axhline(Mvalue, color='green', linestyle='solid')

    plt.text(0.95, 0.05, 'WACC='+str(WACC), horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)
    # 添加标题和标签
    plt.title('EPV value')
    plt.ylabel('Value')

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # 显示图形
    plt.savefig(stockName + '估值.png')
    # 打包四张图片成一个MJPEG格式的HTTP响应
    images = []
    images.append(Image.open(stockName + '.png'))
    images.append(Image.open(stockName + '营收.png'))
    images.append(Image.open(stockName + '获现率.png'))
    images.append(Image.open(stockName + '估值.png'))
    # 拼接四张图片
    width, height = images[0].size
    total_height = height * len(images)
    combined_image = Image.new('RGB', (width, total_height))
    y_offset = 0
    for img in images:
        combined_image.paste(img, (0, y_offset))
        y_offset += height

    # 将拼接后的图片保存为PNG格式
    with io.BytesIO() as output:
        combined_image.save(output, format='PNG')
        image_data = output.getvalue()

    # 将PNG数据编码为base64字符串
    image_data_base64 = base64.b64encode(image_data).decode('ascii')

    # 构造HTTP响应
    boundary_string = 'frame'
    response = b''
    response += b'--' + boundary_string.encode('ascii') + b'\r\n'
    response += b'Content-type: image/png\r\n\r\n'
    response += image_data + b'\r\n'
    response += b'--' + boundary_string.encode('ascii') + b'--\r\n'

    return response
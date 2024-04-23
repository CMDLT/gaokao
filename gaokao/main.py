import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

# 载入数据
data = pd.read_excel('./data/data.xlsx')

df = pd.DataFrame(data)
df = df.drop(columns=["序号", "院校在京招生编码", "专业组码"])

# 用平均数填充‘总分’空值
df['总分'] = df['总分'].fillna(df['总分'].mean())
# 计算每组的均值
mean_values = df.groupby(['院校', '专业类']).mean()
# 计算每组的均值来填充NaN值
def fill_na_with_group_mean(row):
    if pd.isnull(row['总分']):
        return mean_values.loc[row['院校'], row['专业类']]['总分']
    else:
        return row['总分']

df['总分'] = df.apply(fill_na_with_group_mean, axis=1)

# 存储每组的模型
models = {}

# 按学校和专业类分组
grouped_data = df.groupby(['院校', '专业类'])

# 迭代每个学校和专业类组，建立模型
for name, group in grouped_data:
    school, major = name
    X = group['年份'].values.reshape(-1, 1)
    y = group['总分'].values

    # 创建线性回归模型
    model = LinearRegression()

    # 如果样本数量允许进行留一法交叉验证，则进行交叉验证，否则直接使用单一样本进行拟合
    if len(X) > 1:
        cv_scores = cross_val_score(model, X, y, cv=len(X), scoring='neg_mean_squared_error')
        avg_mse = np.mean(cv_scores)
    model.fit(X, y)
    if len(X) == 1:
        y_pred = model.predict(X)
        avg_mse = mean_squared_error(y, y_pred)

    # 存储模型
    models[name] = model

    print(f'学校: {school}, 专业类: {major}, Average Negative Mean Squared Error: {avg_mse}')

# 预测2024年的分数线
predictions = {}

for name, model in models.items():
    school, major = name
    # 预测2024年的总分
    prediction_2024 = model.predict(np.array([[2024]]))[0]
    predictions[name] = prediction_2024
    print(f'学校: {school}, 专业类: {major}, 预测2024年总分: {prediction_2024}')

# 创建DataFrame来保存预测结果
results = pd.DataFrame(predictions, index=['预测2024年总分']).transpose()
results.reset_index(inplace=True)
results.columns = ['学校', '专业类', '预测2024年总分']

# 将结果保存到CSV文件
results.to_csv('预测结果.csv', index=False)
results.to_excel('预测结果.xlsx',index=False)
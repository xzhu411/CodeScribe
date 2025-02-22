# 1.1. 線性模型 (Linear Models)
線性回歸模型的目標是預測值為輸入特徵的線性組合。

## 1.1.1. 最小二乘法 (Ordinary Least Squares)
最小二乘法透過最小化殘差平方和來擬合線性模型。

### 示例
```python
from sklearn import linear_model
reg = linear_model.LinearRegression()
reg.fit([[0, 0], [1, 1], [2, 2]], [0, 1, 2])
print(reg.coef_)  # [0.5, 0.5]

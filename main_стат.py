import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import scipy.stats as stats
import seaborn as sns


def t_test_sklearn(X, y, model, alpha=0.05):
    n = len(y)
    p = X.shape[1]

    y_pred = model.predict(X)
    residuals = y - y_pred
    mse = np.sum(residuals ** 2) / (n - p - 1)

    X_with_const = np.column_stack([np.ones(n), X])
    xtx_inv = np.linalg.inv(X_with_const.T @ X_with_const)

    se = np.sqrt(np.diag(xtx_inv) * mse)
    coefficients = np.append(model.intercept_, model.coef_)
    t_stats = coefficients / se
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - p - 1))

    t_critical = stats.t.ppf(1 - alpha / 2, n - p - 1)
    ci_lower = coefficients - t_critical * se
    ci_upper = coefficients + t_critical * se

    return coefficients, se, t_stats, p_values, ci_lower, ci_upper


def prediction_interval_sklearn_fixed(X, y, model, x_new, alpha=0.05):
    n = len(y)
    p = X.shape[1]

    if len(x_new.shape) == 1:
        x_new = x_new.reshape(1, -1)
    y_pred = model.predict(x_new)[0]

    y_pred_all = model.predict(X)
    residuals = y - y_pred_all
    mse = np.sum(residuals ** 2) / (n - p - 1)

    X_with_const = np.column_stack([np.ones(n), X])
    x_new_with_const = np.append(1, x_new[0])

    xtx_inv = np.linalg.inv(X_with_const.T @ X_with_const)
    var_mean_pred = mse * (x_new_with_const @ xtx_inv @ x_new_with_const.T)
    se_mean_pred = np.sqrt(var_mean_pred)

    var_individual_pred = mse * (1 + x_new_with_const @ xtx_inv @ x_new_with_const.T)
    se_individual_pred = np.sqrt(var_individual_pred)

    t_critical = stats.t.ppf(1 - alpha / 2, n - p - 1)

    ci_lower_mean = y_pred - t_critical * se_mean_pred
    ci_upper_mean = y_pred + t_critical * se_mean_pred
    ci_lower_individual = y_pred - t_critical * se_individual_pred
    ci_upper_individual = y_pred + t_critical * se_individual_pred

    ci_lower_mean = max(ci_lower_mean, 0)
    ci_lower_individual = max(ci_lower_individual, 0)

    return y_pred, ci_lower_mean, ci_upper_mean, ci_lower_individual, ci_upper_individual


def calculate_f_test(y, y_pred, k):
    """Выполняет F-тест для модели"""
    n = len(y)
    r2 = r2_score(y, y_pred)

    if r2 == 1.0:
        return np.inf, 0.0

    f_stat = (r2 / k) / ((1 - r2) / (n - k - 1))
    f_pvalue = 1 - stats.f.cdf(f_stat, k, n - k - 1)

    return f_stat, f_pvalue


def load_and_explore_data():
    """Загружает и анализирует данные"""
    df = pd.read_excel('LAB_6_DATA_2025_PART_1.xlsx', sheet_name='MyList')
    df.columns = ['Стаж', 'Образование', 'Пол', 'Зарплата']
    data = df[['Стаж', 'Образование', 'Пол', 'Зарплата']].copy()
    
    print("\nРазмер данных:", data.shape)
    print("\nПервые 5 строк:")
    print(data.head())
    print("\nОсновные статистики:")
    print(data.describe())
    
    return data


def create_pairplot(data):
    """Создает pairplot для данных"""
    sns.pairplot(data[['Зарплата', 'Стаж', 'Образование']])
    plt.suptitle('Pair Plot: взаимосвязи между переменными', y=1.02)
    plt.show()


def print_header(title, width=50):
    """Печатает заголовок раздела"""
    print("\n" + "=" * width)
    print(title)


def run_simple_regression(data, Z_var, alpha):
    """Выполняет простую регрессию"""
    print_header("ЗАДАНИЕ 1: Оценка параметров модели Зарплата = f(Образование)")
    X1 = data[[Z_var]]
    y = data['Зарплата']

    model1 = LinearRegression()
    model1.fit(X1, y)

    beta0_1 = model1.intercept_
    beta1_1 = model1.coef_[0]
    print(f"Модель 1: Зарплата = {beta0_1:.4f} + {beta1_1:.4f} × Образование")
    
    return model1, X1, y


# Параметры по варианту 13
Z_var = 'Образование'
gamma = 0.915
alpha = 0.085
gender = 0
a = 12
b = 10

print(f"Z: {Z_var}")
print(f"Уровень доверия γ = {gamma}")
print(f"Уровень значимости α = {alpha}")
print(f"Пол (0 = мужчина, 1 = женщина): {gender}")
print(f"Стаж для прогноза (a): {a} лет")
print(f"Образование для прогноза (b): {b} лет")


# Загрузка данных
data = load_and_explore_data()
create_pairplot(data)

# === Задание 1: Простая регрессия Зарплата = f(Образование) ===
model1, X1, y = run_simple_regression(data, Z_var, alpha)


# === Задание 2: F-тест для модели 1 ===
print_header("ЗАДАНИЕ 2: Проверка объясняющей способности модели 1 (F-тест)")

y_pred_1 = model1.predict(X1)
r2_1 = r2_score(y, y_pred_1)

n = len(y)
k1 = 1
f_stat_1, f_pvalue_1 = calculate_f_test(y, y_pred_1, k1)

print(f"R² = {r2_1:.4f}")
print(f"F-статистика = {f_stat_1:.4f}, p-value = {f_pvalue_1:.4e}")

if f_pvalue_1 < alpha:
    print(f"ВЫВОД: Модель статистически значима (p = {f_pvalue_1:.4e} < α = {alpha}).")
    print("Она обладает умеренной объясняющей способностью.")
else:
    print(f"ВЫВОД: Модель статистически НЕ значима (p = {f_pvalue_1:.4e} > α = {alpha}).")
    print("Она считается низкокачественной.")


# === Задание 3: Множественная регрессия ===
print_header("ЗАДАНИЕ 3: Оценка параметров модели Зарплата = f(Стаж, Образование, Пол)")

X2 = data[['Стаж', 'Образование', 'Пол']]
model2 = LinearRegression()
model2.fit(X2, y)

intercept2 = model2.intercept_
coefs2 = model2.coef_
print(f"Модель 2: Зарплата = {intercept2:.4f} + {coefs2[0]:.4f}×Стаж + {coefs2[1]:.4f}×Образование + {coefs2[2]:.4f}×Пол")


# === Задание 4: F-тест для модели 2 ===
print_header("ЗАДАНИЕ 4: Проверка объясняющей способности модели 2 (F-тест)")

y_pred_2 = model2.predict(X2)
r2_2 = r2_score(y, y_pred_2)

k2 = 3
f_stat_2, f_pvalue_2 = calculate_f_test(y, y_pred_2, k2)

print(f"R² = {r2_2:.4f}")
print(f"F-статистика = {f_stat_2:.4f}, p-value = {f_pvalue_2:.4e}")

if f_pvalue_2 < alpha:
    print(f"ВЫВОД: Модель статистически значима в целом (p = {f_pvalue_2:.4e} < α = {alpha}).")
    print("Она обладает умеренной объясняющей способностью.")
else:
    print(f"ВЫВОД: Модель статистически НЕ значима (p = {f_pvalue_2:.4e} > α = {alpha}).")
    print("Она считается низкокачественной.")

print(f"\nСравнение моделей:")
print(f"R² (модель 1): {r2_1:.4f}")
print(f"R² (модель 2): {r2_2:.4f}")
print(f"Улучшение: {(r2_2 - r2_1)*100:.2f}% дополнительной объяснённой дисперсии.")


# === t-тесты для коэффициентов модели 2 ===
coeffs, se, t_stats, p_values, ci_low, ci_up = t_test_sklearn(X2, y, model2, alpha)


# === Задание 5: Гендерный эффект ===
print_header("ЗАДАНИЕ 5: Значимо ли различаются зарплаты мужчин и женщин при прочих равных?")

p_gender = p_values[3]
coef_gender = coeffs[3]

print(f"Коэффициент при 'Пол': β₃ = {coef_gender:.4f}")
print(f"p-value = {p_gender:.4f}")

if p_gender < alpha:
    if coef_gender < 0:
        print(f"ВЫВОД: Женщины в среднем получают на {abs(coef_gender):.2f} долл./час МЕНЬШЕ мужчин (при равных стаже и образовании).")
        print("Различие статистически значимо.")
    else:
        print(f"ВЫВОД: Женщины в среднем получают на {coef_gender:.2f} долл./час БОЛЬШЕ мужчин.")
        print("Различие статистически значимо.")
else:
    print("ВЫВОД: Статистически значимых различий в зарплатах по полу не выявлено.")


# === Задание 6: Стаж ===
print_header("ЗАДАНИЕ 6: Значим ли коэффициент при СТАЖЕ?")

p_stazh = p_values[1]
coef_stazh = coeffs[1]
print(f"Коэффициент при стаже: β₁ = {coef_stazh:.4f}, p-value = {p_stazh:.4f}")

if p_stazh < alpha:
    print("ВЫВОД: Связь между стажем и зарплатой статистически значима и отражает истинную зависимость.")
else:
    print("ВЫВОД: Связь может быть случайной; коэффициент не значим.")


# === Задание 7: Образование ===
print_header("ЗАДАНИЕ 7: Значим ли коэффициент при ОБРАЗОВАНИИ?")

p_edu = p_values[2]
coef_edu = coeffs[2]
print(f"Коэффициент при образовании: β₂ = {coef_edu:.4f}, p-value = {p_edu:.4f}")

if p_edu < alpha:
    print("ВЫВОД: Отдача от дополнительного года образования статистически значима.")
else:
    print("ВЫВОД: Эффект образования не подтверждается данными (коэффициент не значим).")


# === Задание 8: Доверительные интервалы ===
print_header(f"ЗАДАНИЕ 8: Доверительные интервалы для коэффициентов (γ = {gamma})")

print(f"\n{'Параметр':<18} {'Оценка':<10} {'95% ДИ':<30}")
print("-" * 55)
names = ["Константа", "Стаж", "Образование", "Пол"]
for i in range(4):
    print(f"{names[i]:<18} {coeffs[i]:<10.4f} [{ci_low[i]:.4f}, {ci_up[i]:.4f}]")


# === Задание 9: Прогноз ===
print_header("ЗАДАНИЕ 9: Прогноз зарплаты с интервалами")

x_new = np.array([[a, b, gender]])
point, ci_mean_low, ci_mean_up, ci_ind_low, ci_ind_up = prediction_interval_sklearn_fixed(X2, y, model2, x_new, alpha)

print(f"\nХарактеристики работника: стаж = {a} лет, образование = {b} лет, пол = {'мужчина' if gender == 0 else 'женщина'}")
print(f"\nТочечный прогноз: {point:.2f} долл./час")
print(f"Доверительный интервал для СРЕДНЕЙ зарплаты: [{ci_mean_low:.2f}, {ci_mean_up:.2f}]")
print(f"Прогнозный интервал для ИНДИВИДУАЛЬНОЙ зарплаты: [{ci_ind_low:.2f}, {ci_ind_up:.2f}]")


# === Задание 10: +2 года стажа ===
print_header("ЗАДАНИЕ 10: Изменение зарплаты при +2 года стажа")
delta = 2 * coeffs[1]
print(f"ΔЗарплата = 2 × {coeffs[1]:.4f} = {delta:.2f} долл./час")
print(f"ВЫВОД: При прочих равных зарплата увеличится в среднем на {delta:.2f} долл./час.")


# === Задание 11: +1 год образования ===
print_header("ЗАДАНИЕ 11: Прибавка за +1 год образования")
print(f"Каждый дополнительный год образования даёт +{coeffs[2]:.2f} долл./час.")


# === Задание 12: Дискриминация? ===
print_header("ЗАДАНИЕ 12: Имеет ли место гендерная дискриминация?")

if p_gender < alpha and coef_gender < 0:
    print("ВЫВОД: Да, имеются статистически значимые признаки дискриминации против женщин.")
elif p_gender < alpha and coef_gender > 0:
    print("ВЫВОД: Дискриминации против женщин нет; наоборот, женщины получают больше.")
else:
    print("ВЫВОД: Нет статистических доказательств гендерной дискриминации.")


# === ИТОГ ===
print("\n" + "=" * 60)
print("ИТОГОВЫЙ ВЫВОД")
print("-" * 60)
print(f"• Множественная модель значима (p = {f_pvalue_2:.2e} < {alpha}) и объясняет {r2_2*100:.1f}% дисперсии.")
print(f"• Образование и стаж положительно влияют на зарплату и значимы.")
print(f"• Пол: ", end="")
if p_gender < alpha:
    if coef_gender < 0:
        print(f"женщины получают на {abs(coef_gender):.2f} долл./час меньше → возможна дискриминация.")
    else:
        print(f"женщины получают больше → дискриминации нет.")
else:
    print("статистически значимых различий нет.")
print("="*60)

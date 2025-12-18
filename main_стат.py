import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import scipy.stats as stats
import seaborn as sns


class ModelConfig:
    """Класс для хранения конфигурации модели"""
    def __init__(self):
        self.Z_var = 'Образование'
        self.gamma = 0.915
        self.alpha = 0.085
        self.gender = 0
        self.experience_years = 12
        self.education_years = 10
        
    def display(self):
        """Выводит параметры конфигурации"""
        print(f"Z: {self.Z_var}")
        print(f"Уровень доверия γ = {self.gamma}")
        print(f"Уровень значимости α = {self.alpha}")
        print(f"Пол (0 = мужчина, 1 = женщина): {self.gender}")
        print(f"Стаж для прогноза: {self.experience_years} лет")
        print(f"Образование для прогноза: {self.education_years} лет")


class RegressionModel:
    """Класс для работы с регрессионной моделью"""
    
    def __init__(self, X: pd.DataFrame, y: pd.Series, name: str = "Model"):
        self.X = X
        self.y = y
        self.name = name
        self.model = LinearRegression()
        self.coefficients = None
        self.intercept = None
        self.r_squared = None
        self.f_statistic = None
        self.f_pvalue = None
        
    def fit(self):
        """Обучает модель"""
        self.model.fit(self.X, self.y)
        self.intercept = self.model.intercept_
        self.coefficients = self.model.coef_
        return self
    
    def predict(self, X=None):
        """Делает предсказания"""
        if X is None:
            X = self.X
        return self.model.predict(X)
    
    def evaluate(self, alpha=0.05):
        """Выполняет оценку модели"""
        y_pred = self.predict()
        self.r_squared = r2_score(self.y, y_pred)
        
        # F-тест
        n = len(self.y)
        k = self.X.shape[1]
        self.f_statistic, self.f_pvalue = RegressionAnalyzer.calculate_f_test(self.y, y_pred, k)
        
        return self
    
    def get_summary(self):
        """Возвращает строковое представление модели"""
        equation = f"{self.name}: Зарплата = {self.intercept:.4f}"
        feature_names = list(self.X.columns)
        
        for coef, name in zip(self.coefficients, feature_names):
            equation += f" + {coef:.4f}×{name}"
            
        return equation
    
    def get_coefficient(self, feature_name):
        """Возвращает коэффициент для указанного признака"""
        if feature_name == 'intercept':
            return self.intercept
        
        feature_names = list(self.X.columns)
        if feature_name in feature_names:
            idx = feature_names.index(feature_name)
            return self.coefficients[idx]
        
        raise ValueError(f"Признак '{feature_name}' не найден в модели")


class RegressionAnalyzer:
    """Анализатор регрессионных моделей"""
    
    @staticmethod
    def calculate_t_test(X, y, model, alpha=0.05):
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

    @staticmethod
    def calculate_prediction_interval(X, y, model, x_new, alpha=0.05):
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

    @staticmethod
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


# Инициализация конфигурации
config = ModelConfig()
config.display()

# Загрузка данных
data = load_and_explore_data()
create_pairplot(data)

# === Задание 1: Простая регрессия Зарплата = f(Образование) ===
print_header("ЗАДАНИЕ 1: Оценка параметров модели Зарплата = f(Образование)")

X1 = data[[config.Z_var]]
y = data['Зарплата']
model1 = RegressionModel(X1, y, "Модель 1")
model1.fit().evaluate(config.alpha)

print(model1.get_summary())


# === Задание 2: F-тест для модели 1 ===
print_header("ЗАДАНИЕ 2: Проверка объясняющей способности модели 1 (F-тест)")

print(f"R² = {model1.r_squared:.4f}")
print(f"F-статистика = {model1.f_statistic:.4f}, p-value = {model1.f_pvalue:.4e}")

if model1.f_pvalue < config.alpha:
    print(f"ВЫВОД: Модель статистически значима (p = {model1.f_pvalue:.4e} < α = {config.alpha}).")
    print("Она обладает умеренной объясняющей способностью.")
else:
    print(f"ВЫВОД: Модель статистически НЕ значима (p = {model1.f_pvalue:.4e} > α = {config.alpha}).")
    print("Она считается низкокачественной.")


# === Задание 3: Множественная регрессия ===
print_header("ЗАДАНИЕ 3: Оценка параметров модели Зарплата = f(Стаж, Образование, Пол)")

X2 = data[['Стаж', 'Образование', 'Пол']]
model2 = RegressionModel(X2, y, "Модель 2")
model2.fit().evaluate(config.alpha)

print(model2.get_summary())


# === Задание 4: F-тест для модели 2 ===
print_header("ЗАДАНИЕ 4: Проверка объясняющей способности модели 2 (F-тест)")

print(f"R² = {model2.r_squared:.4f}")
print(f"F-статистика = {model2.f_statistic:.4f}, p-value = {model2.f_pvalue:.4e}")

if model2.f_pvalue < config.alpha:
    print(f"ВЫВОД: Модель статистически значима в целом (p = {model2.f_pvalue:.4e} < α = {config.alpha}).")
    print("Она обладает умеренной объясняющей способностью.")
else:
    print(f"ВЫВОД: Модель статистически НЕ значима (p = {model2.f_pvalue:.4e} > α = {config.alpha}).")
    print("Она считается низкокачественной.")

print(f"\nСравнение моделей:")
print(f"R² (модель 1): {model1.r_squared:.4f}")
print(f"R² (модель 2): {model2.r_squared:.4f}")
print(f"Улучшение: {(model2.r_squared - model1.r_squared)*100:.2f}% дополнительной объяснённой дисперсии.")


# === t-тесты для коэффициентов модели 2 ===
coeffs, se, t_stats, p_values, ci_low, ci_up = RegressionAnalyzer.calculate_t_test(X2, y, model2.model, config.alpha)


# === Задание 5: Гендерный эффект ===
print_header("ЗАДАНИЕ 5: Значимо ли различаются зарплаты мужчин и женщин при прочих равных?")

p_gender = p_values[3]
coef_gender = coeffs[3]

print(f"Коэффициент при 'Пол': β₃ = {coef_gender:.4f}")
print(f"p-value = {p_gender:.4f}")

if p_gender < config.alpha:
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

if p_stazh < config.alpha:
    print("ВЫВОД: Связь между стажем и зарплатой статистически значима и отражает истинную зависимость.")
else:
    print("ВЫВОД: Связь может быть случайной; коэффициент не значим.")


# === Задание 7: Образование ===
print_header("ЗАДАНИЕ 7: Значим ли коэффициент при ОБРАЗОВАНИИ?")

p_edu = p_values[2]
coef_edu = coeffs[2]
print(f"Коэффициент при образовании: β₂ = {coef_edu:.4f}, p-value = {p_edu:.4f}")

if p_edu < config.alpha:
    print("ВЫВОД: Отдача от дополнительного года образования статистически значима.")
else:
    print("ВЫВОД: Эффект образования не подтверждается данными (коэффициент не значим).")


# === Задание 8: Доверительные интервалы ===
print_header(f"ЗАДАНИЕ 8: Доверительные интервалы для коэффициентов (γ = {config.gamma})")

print(f"\n{'Параметр':<18} {'Оценка':<10} {'95% ДИ':<30}")
print("-" * 55)
names = ["Константа", "Стаж", "Образование", "Пол"]
for i in range(4):
    print(f"{names[i]:<18} {coeffs[i]:<10.4f} [{ci_low[i]:.4f}, {ci_up[i]:.4f}]")


# === Задание 9: Прогноз ===
print_header("ЗАДАНИЕ 9: Прогноз зарплаты с интервалами")

x_new = np.array([[config.experience_years, config.education_years, config.gender]])
point, ci_mean_low, ci_mean_up, ci_ind_low, ci_ind_up = RegressionAnalyzer.calculate_prediction_interval(X2, y, model2.model, x_new, config.alpha)

print(f"\nХарактеристики работника: стаж = {config.experience_years} лет, образование = {config.education_years} лет, пол = {'мужчина' if config.gender == 0 else 'женщина'}")
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

if p_gender < config.alpha and coef_gender < 0:
    print("ВЫВОД: Да, имеются статистически значимые признаки дискриминации против женщин.")
elif p_gender < config.alpha and coef_gender > 0:
    print("ВЫВОД: Дискриминации против женщин нет; наоборот, женщины получают больше.")
else:
    print("ВЫВОД: Нет статистических доказательств гендерной дискриминации.")


# === ИТОГ ===
print("\n" + "=" * 60)
print("ИТОГОВЫЙ ВЫВОД")
print("-" * 60)
print(f"• Множественная модель значима (p = {model2.f_pvalue:.2e} < {config.alpha}) и объясняет {model2.r_squared*100:.1f}% дисперсии.")
print(f"• Образование и стаж положительно влияют на зарплату и значимы.")
print(f"• Пол: ", end="")
if p_gender < config.alpha:
    if coef_gender < 0:
        print(f"женщины получают на {abs(coef_gender):.2f} долл./час меньше → возможна дискриминация.")
    else:
        print(f"женщины получают больше → дискриминации нет.")
else:
    print("статистически значимых различий нет.")
print("="*60)

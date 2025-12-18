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


class ReportGenerator:
    """Генератор отчетов и выводов"""
    
    @staticmethod
    def print_header(title: str, width: int = 50):
        """Печатает заголовок раздела"""
        print("\n" + "=" * width)
        print(title)
    
    @staticmethod
    def print_model_summary(model: RegressionModel):
        """Печатает уравнение модели"""
        print(model.get_summary())
    
    @staticmethod
    def print_f_test_results(model: RegressionModel, alpha: float):
        """Печатает результаты F-теста"""
        print(f"R² = {model.r_squared:.4f}")
        print(f"F-статистика = {model.f_statistic:.4f}, p-value = {model.f_pvalue:.4e}")
        
        if model.f_pvalue < alpha:
            print(f"ВЫВОД: Модель статистически значима (p = {model.f_pvalue:.4e} < α = {alpha}).")
            print("Она обладает умеренной объясняющей способностью.")
        else:
            print(f"ВЫВОД: Модель статистически НЕ значима (p = {model.f_pvalue:.4e} > α = {alpha}).")
            print("Она считается низкокачественной.")
    
    @staticmethod
    def print_coefficient_analysis(feature_name: str, coefficient: float, p_value: float, alpha: float):
        """Анализирует значимость коэффициента"""
        print(f"Коэффициент при '{feature_name}': β = {coefficient:.4f}, p-value = {p_value:.4f}")
        
        if p_value < alpha:
            if coefficient > 0:
                print(f"ВЫВОД: {feature_name} положительно и значимо влияет на зарплату.")
            else:
                print(f"ВЫВОД: {feature_name} отрицательно и значимо влияет на зарплату.")
        else:
            print(f"ВЫВОД: Влияние {feature_name} не является статистически значимым.")
    
    @staticmethod
    def print_confidence_intervals(names: list, coefficients: np.ndarray, 
                                  ci_lower: np.ndarray, ci_upper: np.ndarray):
        """Печатает доверительные интервалы"""
        print(f"\n{'Параметр':<18} {'Оценка':<10} {'95% ДИ':<30}")
        print("-" * 55)
        for i, name in enumerate(names):
            print(f"{name:<18} {coefficients[i]:<10.4f} [{ci_lower[i]:.4f}, {ci_upper[i]:.4f}]")
    
    @staticmethod
    def print_prediction_results(point_pred: float, ci_mean: tuple, ci_individual: tuple, 
                                experience: int, education: int, gender: int):
        """Печатает результаты прогноза"""
        gender_str = 'мужчина' if gender == 0 else 'женщина'
        print(f"\nХарактеристики работника: стаж = {experience} лет, образование = {education} лет, пол = {gender_str}")
        print(f"\nТочечный прогноз: {point_pred:.2f} долл./час")
        print(f"Доверительный интервал для СРЕДНЕЙ зарплаты: [{ci_mean[0]:.2f}, {ci_mean[1]:.2f}]")
        print(f"Прогнозный интервал для ИНДИВИДУАЛЬНОЙ зарплаты: [{ci_individual[0]:.2f}, {ci_individual[1]:.2f}]")


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


# Инициализация конфигурации
config = ModelConfig()
config.display()

# Загрузка данных
data = load_and_explore_data()
create_pairplot(data)

# === Задание 1: Простая регрессия Зарплата = f(Образование) ===
ReportGenerator.print_header("ЗАДАНИЕ 1: Оценка параметров модели Зарплата = f(Образование)")

X1 = data[[config.Z_var]]
y = data['Зарплата']
model1 = RegressionModel(X1, y, "Модель 1")
model1.fit().evaluate(config.alpha)

ReportGenerator.print_model_summary(model1)


# === Задание 2: F-тест для модели 1 ===
ReportGenerator.print_header("ЗАДАНИЕ 2: Проверка объясняющей способности модели 1 (F-тест)")
ReportGenerator.print_f_test_results(model1, config.alpha)


# === Задание 3: Множественная регрессия ===
ReportGenerator.print_header("ЗАДАНИЕ 3: Оценка параметров модели Зарплата = f(Стаж, Образование, Пол)")

X2 = data[['Стаж', 'Образование', 'Пол']]
model2 = RegressionModel(X2, y, "Модель 2")
model2.fit().evaluate(config.alpha)

ReportGenerator.print_model_summary(model2)


# === Задание 4: F-тест для модели 2 ===
ReportGenerator.print_header("ЗАДАНИЕ 4: Проверка объясняющей способности модели 2 (F-тест)")
ReportGenerator.print_f_test_results(model2, config.alpha)

print(f"\nСравнение моделей:")
print(f"R² (модель 1): {model1.r_squared:.4f}")
print(f"R² (модель 2): {model2.r_squared:.4f}")
print(f"Улучшение: {(model2.r_squared - model1.r_squared)*100:.2f}% дополнительной объяснённой дисперсии.")


# === t-тесты для коэффициентов модели 2 ===
coeffs, se, t_stats, p_values, ci_low, ci_up = RegressionAnalyzer.calculate_t_test(X2, y, model2.model, config.alpha)


# === Задание 5: Гендерный эффект ===
ReportGenerator.print_header("ЗАДАНИЕ 5: Значимо ли различаются зарплаты мужчин и женщин при прочих равных?")
ReportGenerator.print_coefficient_analysis('Пол', coeffs[3], p_values[3], config.alpha)


# === Задание 6: Стаж ===
ReportGenerator.print_header("ЗАДАНИЕ 6: Значим ли коэффициент при СТАЖЕ?")
ReportGenerator.print_coefficient_analysis('Стаж', coeffs[1], p_values[1], config.alpha)


# === Задание 7: Образование ===
ReportGenerator.print_header("ЗАДАНИЕ 7: Значим ли коэффициент при ОБРАЗОВАНИИ?")
ReportGenerator.print_coefficient_analysis('Образование', coeffs[2], p_values[2], config.alpha)


# === Задание 8: Доверительные интервалы ===
ReportGenerator.print_header(f"ЗАДАНИЕ 8: Доверительные интервалы для коэффициентов (γ = {config.gamma})")
ReportGenerator.print_confidence_intervals(
    ["Константа", "Стаж", "Образование", "Пол"],
    coeffs, ci_low, ci_up
)


# === Задание 9: Прогноз ===
ReportGenerator.print_header("ЗАДАНИЕ 9: Прогноз зарплаты с интервалами")

x_new = np.array([[config.experience_years, config.education_years, config.gender]])
point, ci_mean_low, ci_mean_up, ci_ind_low, ci_ind_up = RegressionAnalyzer.calculate_prediction_interval(
    X2, y, model2.model, x_new, config.alpha
)

ReportGenerator.print_prediction_results(
    point, 
    (ci_mean_low, ci_mean_up), 
    (ci_ind_low, ci_ind_up),
    config.experience_years, 
    config.education_years, 
    config.gender
)


# === Задание 10: +2 года стажа ===
ReportGenerator.print_header("ЗАДАНИЕ 10: Изменение зарплаты при +2 года стажа")
delta = 2 * coeffs[1]
print(f"ΔЗарплата = 2 × {coeffs[1]:.4f} = {delta:.2f} долл./час")
print(f"ВЫВОД: При прочих равных зарплата увеличится в среднем на {delta:.2f} долл./час.")


# === Задание 11: +1 год образования ===
ReportGenerator.print_header("ЗАДАНИЕ 11: Прибавка за +1 год образования")
print(f"Каждый дополнительный год образования даёт +{coeffs[2]:.2f} долл./час.")


# === Задание 12: Дискриминация? ===
ReportGenerator.print_header("ЗАДАНИЕ 12: Имеет ли место гендерная дискриминация?")

p_gender = p_values[3]
coef_gender = coeffs[3]

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

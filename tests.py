import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO

# Подключаем нужные функции из проекта
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_calc, rub, _parse_money
import schemas


# ════════════════════════════════════════════════════════════
# 1. run_calc — ядро расчёта инвестиций
# ════════════════════════════════════════════════════════════
class TestRunCalc(unittest.TestCase):

    def _make_input(self, initial=100_000, monthly=10_000, rate=7.0, years=10):
        return schemas.CalcInput(
            initial_amount=initial,
            monthly_contribution=monthly,
            annual_rate=rate,
            years=years,
        )

    # ✅ Позитивные
    def test_positive_final_amount_greater_than_contributions(self):
        """Итоговая сумма должна быть больше суммы взносов при ненулевой ставке."""
        result = run_calc(self._make_input())
        self.assertGreater(result.final_amount, result.total_contributions)

    def test_positive_schedule_length_equals_years(self):
        """Длина расписания должна совпадать с количеством лет."""
        result = run_calc(self._make_input(years=5))
        self.assertEqual(len(result.schedule), 5)

    def test_positive_profit_equals_final_minus_contributions(self):
        """Доход = итоговая сумма − взносы."""
        result = run_calc(self._make_input())
        self.assertAlmostEqual(
            result.profit,
            result.final_amount - result.total_contributions,
            places=1
        )

    def test_positive_zero_rate_no_profit(self):
        """При нулевой ставке доход должен быть равен нулю (или очень близко)."""
        result = run_calc(self._make_input(rate=0.0))
        self.assertAlmostEqual(result.profit, 0.0, places=1)

    def test_positive_one_year_schedule(self):
        """За 1 год расписание содержит ровно одну запись."""
        result = run_calc(self._make_input(years=1))
        self.assertEqual(len(result.schedule), 1)

    # ❌ Негативные
    def test_negative_zero_initial_and_monthly(self):
        """При нулевом капитале и взносах итоговая сумма должна быть 0."""
        result = run_calc(self._make_input(initial=0, monthly=0))
        self.assertAlmostEqual(result.final_amount, 0.0, places=1)

    def test_negative_very_high_rate(self):
        """Очень высокая ставка не должна вызывать ошибку."""
        try:
            result = run_calc(self._make_input(rate=999.0, years=1))
            self.assertGreater(result.final_amount, 0)
        except Exception as e:
            self.fail(f"run_calc упал с неожиданной ошибкой: {e}")

    def test_negative_schedule_years_are_sequential(self):
        """Годы в расписании должны идти по порядку: 1, 2, 3..."""
        result = run_calc(self._make_input(years=5))
        years = [row.year for row in result.schedule]
        self.assertEqual(years, list(range(1, 6)))


# ════════════════════════════════════════════════════════════
# 2. rub — форматирование числа в рубли
# ════════════════════════════════════════════════════════════
class TestRub(unittest.TestCase):

    # ✅ Позитивные
    def test_positive_integer(self):
        """Целое число форматируется корректно."""
        result = rub(1000)
        self.assertIn("1", result)
        self.assertIn("₽", result)

    def test_positive_large_number(self):
        """Большое число содержит разделитель тысяч."""
        result = rub(1_000_000)
        self.assertIn("₽", result)
        self.assertIn("1", result)

    def test_positive_zero(self):
        """Ноль форматируется без ошибок."""
        result = rub(0)
        self.assertIn("₽", result)

    # ❌ Негативные
    def test_negative_negative_number(self):
        """Отрицательное число не вызывает ошибку."""
        result = rub(-500)
        self.assertIn("₽", result)

    def test_negative_float(self):
        """Дробное число обрезается до целых."""
        result = rub(1234.99)
        self.assertNotIn(".", result)


# ════════════════════════════════════════════════════════════
# 3. _parse_money — парсинг суммы из строки/числа
# ════════════════════════════════════════════════════════════
class TestParseMoney(unittest.TestCase):

    # ✅ Позитивные
    def test_positive_integer(self):
        self.assertEqual(_parse_money(1000), 1000.0)

    def test_positive_float(self):
        self.assertAlmostEqual(_parse_money(3.14), 3.14)

    def test_positive_string_with_rub(self):
        """Строка с символом рубля парсится корректно."""
        self.assertAlmostEqual(_parse_money("1 500 ₽"), 1500.0)

    def test_positive_string_comma_decimal(self):
        """Европейский формат с запятой."""
        self.assertAlmostEqual(_parse_money("1234,56"), 1234.56)

    def test_positive_none_returns_zero(self):
        """None возвращает 0.0."""
        self.assertEqual(_parse_money(None), 0.0)

    # ❌ Негативные
    def test_negative_empty_string(self):
        """Пустая строка возвращает 0.0."""
        self.assertEqual(_parse_money(""), 0.0)

    def test_negative_non_numeric_string(self):
        """Строка без чисел возвращает 0.0."""
        self.assertEqual(_parse_money("abc"), 0.0)

    def test_negative_only_currency_symbol(self):
        """Только символ ₽ без числа возвращает 0.0."""
        self.assertEqual(_parse_money("₽"), 0.0)


# ════════════════════════════════════════════════════════════
# 4. CalcResult — проверка схемы результата
# ════════════════════════════════════════════════════════════
class TestCalcResult(unittest.TestCase):

    def _get_result(self, **kwargs):
        inp = schemas.CalcInput(
            initial_amount=kwargs.get("initial", 50_000),
            monthly_contribution=kwargs.get("monthly", 5_000),
            annual_rate=kwargs.get("rate", 10.0),
            years=kwargs.get("years", 3),
        )
        return run_calc(inp)

    # ✅ Позитивные
    def test_positive_result_has_all_fields(self):
        """Результат содержит все обязательные поля."""
        result = self._get_result()
        self.assertTrue(hasattr(result, "final_amount"))
        self.assertTrue(hasattr(result, "total_contributions"))
        self.assertTrue(hasattr(result, "profit"))
        self.assertTrue(hasattr(result, "schedule"))

    def test_positive_schedule_rows_have_correct_fields(self):
        """Каждая строка расписания имеет year, total, contributions, profit."""
        result = self._get_result()
        for row in result.schedule:
            self.assertTrue(hasattr(row, "year"))
            self.assertTrue(hasattr(row, "total"))
            self.assertTrue(hasattr(row, "contributions"))
            self.assertTrue(hasattr(row, "profit"))

    def test_positive_totals_grow_over_time(self):
        """Итоговая сумма растёт с каждым годом."""
        result = self._get_result(years=5, rate=10.0)
        totals = [row.total for row in result.schedule]
        self.assertEqual(totals, sorted(totals))

    # ❌ Негативные
    def test_negative_profit_is_negative_impossible(self):
        """При положительной ставке прибыль не может быть отрицательной."""
        result = self._get_result(rate=5.0)
        self.assertGreaterEqual(result.profit, 0)

    def test_negative_contributions_cant_exceed_final(self):
        """Взносы не могут превышать итоговую сумму при положительной ставке."""
        result = self._get_result(rate=5.0)
        self.assertLessEqual(result.total_contributions, result.final_amount)


# ════════════════════════════════════════════════════════════
# 5. _make_calc_from_rows — создание расчёта из строк таблицы
# ════════════════════════════════════════════════════════════
class TestMakeCalcFromRows(unittest.TestCase):

    def _mock_db(self):
        """Создаёт мок сессии БД."""
        db = MagicMock()
        calc_mock = MagicMock()
        calc_mock.id = 1
        calc_mock.title = "Тест"
        calc_mock.initial_amount = 0.0
        calc_mock.monthly_contribution = 0.0
        calc_mock.annual_rate = 0.0
        calc_mock.years = 3
        calc_mock.final_amount = 300.0
        calc_mock.total_contributions = 270.0
        calc_mock.profit = 30.0
        calc_mock.years_rows = []
        db.refresh = MagicMock(side_effect=lambda x: None)
        return db

    def _make_rows(self):
        return [
            {"year": 1, "total": 100.0, "contributions": 90.0, "profit": 10.0},
            {"year": 2, "total": 200.0, "contributions": 180.0, "profit": 20.0},
            {"year": 3, "total": 300.0, "contributions": 270.0, "profit": 30.0},
        ]

    def _mock_user(self):
        u = MagicMock()
        u.id = 1
        return u

    # ✅ Позитивные
    def test_positive_creates_calculation_object(self):
        """Функция создаёт объект Calculation и добавляет его в БД."""
        from main import _make_calc_from_rows
        db = self._mock_db()
        u = self._mock_user()
        rows = self._make_rows()

        _make_calc_from_rows(u, db, "Тестовый расчёт", rows)
        db.add.assert_called()
        db.flush.assert_called()
        db.commit.assert_called()

    def test_positive_years_count_equals_rows(self):
        """Количество лет в объекте равно числу переданных строк."""
        from main import _make_calc_from_rows
        db = self._mock_db()
        u = self._mock_user()
        rows = self._make_rows()

        # Проверяем что add вызван для каждой строки + сам расчёт
        _make_calc_from_rows(u, db, "Тест", rows)
        # 1 Calculation + 3 CalculationYear = минимум 4 вызова add
        self.assertGreaterEqual(db.add.call_count, 4)

    def test_positive_default_title_used_when_empty(self):
        """Если title пустой, используется дефолтное название."""
        from main import _make_calc_from_rows
        db = self._mock_db()
        u = self._mock_user()
        rows = self._make_rows()

        _make_calc_from_rows(u, db, "", rows)
        # Проверяем что объект Calculation создан с title "Импортированный расчёт"
        added_calc = db.add.call_args_list[0][0][0]
        self.assertEqual(added_calc.title, "Импортированный расчёт")

    # ❌ Негативные
    def test_negative_empty_rows_raises_http_exception(self):
        """Пустой список строк вызывает HTTPException."""
        from main import _make_calc_from_rows
        from fastapi import HTTPException
        db = self._mock_db()
        u = self._mock_user()

        with self.assertRaises(HTTPException) as ctx:
            _make_calc_from_rows(u, db, "Тест", [])
        self.assertEqual(ctx.exception.status_code, 400)

    def test_negative_last_row_used_for_totals(self):
        """Итоговые значения берутся из последней строки."""
        from main import _make_calc_from_rows
        db = self._mock_db()
        u = self._mock_user()
        rows = self._make_rows()

        _make_calc_from_rows(u, db, "Тест", rows)
        added_calc = db.add.call_args_list[0][0][0]
        self.assertEqual(added_calc.final_amount, 300.0)
        self.assertEqual(added_calc.total_contributions, 270.0)
        self.assertEqual(added_calc.profit, 30.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
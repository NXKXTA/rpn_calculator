"""Tests for the RPN calculator."""

import unittest

from calculator import (
    CalculatorError,
    calculate,
    evaluate_rpn,
    infix_to_rpn,
    tokenize,
)


class TokenizeTests(unittest.TestCase):
    def test_tokenize_expression(self) -> None:
        self.assertEqual(
            tokenize("12 + 3.5 * (7 - 2)"),
            ["12", "+", "3.5", "*", "(", "7", "-", "2", ")"],
        )

    def test_tokenize_leading_decimal_point(self) -> None:
        self.assertEqual(tokenize(".5 + 1"), [".5", "+", "1"])

    def test_tokenize_trailing_decimal_point(self) -> None:
        self.assertEqual(tokenize("5. + 1"), ["5.", "+", "1"])

    def test_tokenize_invalid_character(self) -> None:
        with self.assertRaises(CalculatorError):
            tokenize("2 & 3")

    def test_tokenize_multiple_decimal_points(self) -> None:
        with self.assertRaises(CalculatorError):
            tokenize("1.2.3")


class ConversionTests(unittest.TestCase):
    def test_basic_conversion(self) -> None:
        self.assertEqual(infix_to_rpn("2 + 3 * 4"), ["2", "3", "4", "*", "+"])

    def test_parentheses_conversion(self) -> None:
        self.assertEqual(
            infix_to_rpn("(2 + 3) * 4"), ["2", "3", "+", "4", "*"]
        )

    def test_subtraction_is_left_associative(self) -> None:
        self.assertEqual(infix_to_rpn("8 - 3 - 1"), ["8", "3", "-", "1", "-"])

    def test_power_is_right_associative(self) -> None:
        self.assertEqual(infix_to_rpn("2 ^ 3 ^ 2"), ["2", "3", "2", "^", "^"])

    def test_unary_minus_and_power_precedence(self) -> None:
        self.assertEqual(infix_to_rpn("-2 ^ 2"), ["2", "2", "^", "u-"])

    def test_negative_exponent_conversion(self) -> None:
        self.assertEqual(infix_to_rpn("2 ^ -2"), ["2", "2", "u-", "^"])

    def test_unmatched_parenthesis(self) -> None:
        with self.assertRaises(CalculatorError):
            infix_to_rpn("(2 + 3")

    def test_implicit_multiplication_is_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            infix_to_rpn("2(3 + 4)")

    def test_empty_expression_is_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            infix_to_rpn("   ")


class EvaluationTests(unittest.TestCase):
    def test_addition(self) -> None:
        self.assertEqual(calculate("2 + 3"), 5)

    def test_operator_precedence(self) -> None:
        self.assertEqual(calculate("2 + 3 * 4"), 14)

    def test_parentheses(self) -> None:
        self.assertEqual(calculate("(2 + 3) * 4"), 20)

    def test_division(self) -> None:
        self.assertEqual(calculate("7 / 2"), 3.5)

    def test_modulo(self) -> None:
        self.assertEqual(calculate("10 % 3"), 1)

    def test_power(self) -> None:
        self.assertEqual(calculate("2 ^ 5"), 32)

    def test_negative_power(self) -> None:
        self.assertEqual(calculate("2 ^ -2"), 0.25)

    def test_power_associativity(self) -> None:
        self.assertEqual(calculate("2 ^ 3 ^ 2"), 512)

    def test_unary_minus_precedence(self) -> None:
        self.assertEqual(calculate("-2 ^ 2"), -4)

    def test_repeated_unary_operators(self) -> None:
        self.assertEqual(calculate("--5 + -+2"), 3)

    def test_decimal_numbers(self) -> None:
        self.assertAlmostEqual(calculate("0.1 + 0.2"), 0.3)

    def test_division_by_zero(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("10 / 0")

    def test_modulo_by_zero(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("10 % 0")

    def test_fractional_exponent_is_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("2 ^ 0.5")

    def test_zero_to_negative_power_is_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("0 ^ -1")

    def test_invalid_expression_is_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate("2 + * 3")

    def test_rpn_requires_exactly_one_result(self) -> None:
        with self.assertRaises(CalculatorError):
            evaluate_rpn(["2", "3"])

    def test_rpn_requires_enough_operands(self) -> None:
        with self.assertRaises(CalculatorError):
            evaluate_rpn(["+"])


if __name__ == "__main__":
    unittest.main()

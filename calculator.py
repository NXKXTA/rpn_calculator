from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

Number: TypeAlias = int | float


class CalculatorError(ValueError):
    """Raise если выражение не парсится"""


@dataclass(frozen=True)
class Operator:
    precedence: int
    associativity: str
    arity: int


OPERATORS: dict[str, Operator] = {
    "+": Operator(precedence=1, associativity="left", arity=2),
    "-": Operator(precedence=1, associativity="left", arity=2),
    "*": Operator(precedence=2, associativity="left", arity=2),
    "/": Operator(precedence=2, associativity="left", arity=2),
    "%": Operator(precedence=2, associativity="left", arity=2),
    "u+": Operator(precedence=3, associativity="right", arity=1),
    "u-": Operator(precedence=3, associativity="right", arity=1),
    "^": Operator(precedence=4, associativity="right", arity=2),
}


def tokenize(expression: str) -> list[str]:
    """Split an expression into numbers, operators and parentheses."""
    tokens: list[str] = []
    index = 0

    while index < len(expression):
        character = expression[index]

        if character.isspace():
            index += 1
            continue

        if "0" <= character <= "9" or character == ".":
            start = index
            dot_count = 0
            digit_count = 0

            while index < len(expression):
                current = expression[index]
                if "0" <= current <= "9":
                    digit_count += 1
                    index += 1
                elif current == ".":
                    dot_count += 1
                    if dot_count > 1:
                        raise CalculatorError(
                            f"Некорректное число около позиции {index + 1}."
                        )
                    index += 1
                else:
                    break

            if digit_count == 0:
                raise CalculatorError(
                    f"Некорректное число около позиции {start + 1}."
                )

            tokens.append(expression[start:index])
            continue

        if character in "+-*/%^()":
            tokens.append(character)
            index += 1
            continue

        raise CalculatorError(
            f"Недопустимый символ '{character}' в позиции {index + 1}."
        )

    return tokens


def infix_to_rpn(expression: str) -> list[str]:
    """Convert an infix expression to RPN using the shunting-yard algorithm."""
    tokens = tokenize(expression)
    if not tokens:
        raise CalculatorError("Выражение пустое.")

    output: list[str] = []
    operator_stack: list[str] = []
    expecting_operand = True

    for token in tokens:
        if _is_number(token):
            if not expecting_operand:
                raise CalculatorError("Между числами отсутствует оператор.")
            output.append(token)
            expecting_operand = False
            continue

        if token == "(":
            if not expecting_operand:
                raise CalculatorError("Перед скобкой отсутствует оператор.")
            operator_stack.append(token)
            expecting_operand = True
            continue

        if token == ")":
            if expecting_operand:
                raise CalculatorError("Пустые скобки или отсутствует операнд.")

            while operator_stack and operator_stack[-1] != "(":
                output.append(operator_stack.pop())

            if not operator_stack:
                raise CalculatorError("Не найдена открывающая скобка.")

            operator_stack.pop()
            expecting_operand = False
            continue

        if expecting_operand:
            if token not in "+-":
                raise CalculatorError(
                    f"Оператор '{token}' не может стоять здесь."
                )
            operator_stack.append("u+" if token == "+" else "u-")
            continue

        current_operator = OPERATORS[token]
        while operator_stack and operator_stack[-1] != "(":
            top_operator = OPERATORS[operator_stack[-1]]
            should_pop = (
                top_operator.precedence > current_operator.precedence
                or (
                    top_operator.precedence == current_operator.precedence
                    and current_operator.associativity == "left"
                )
            )
            if not should_pop:
                break
            output.append(operator_stack.pop())

        operator_stack.append(token)
        expecting_operand = True

    if expecting_operand:
        raise CalculatorError("Выражение не может заканчиваться оператором.")

    while operator_stack:
        operator = operator_stack.pop()
        if operator == "(":
            raise CalculatorError("Не найдена закрывающая скобка.")
        output.append(operator)

    return output


def evaluate_rpn(tokens: list[str]) -> Number:
    """Evaluate an RPN expression using an operand stack."""
    stack: list[Number] = []

    for token in tokens:
        if _is_number(token):
            stack.append(_parse_number(token))
            continue

        if token not in OPERATORS:
            raise CalculatorError(f"Неизвестный элемент ОПЗ: '{token}'.")

        operator = OPERATORS[token]
        if len(stack) < operator.arity:
            raise CalculatorError("Для операции недостаточно операндов.")

        if operator.arity == 1:
            operand = stack.pop()
            if token == "u-":
                stack.append(-operand)
            else:
                stack.append(+operand)
            continue

        right = stack.pop()
        left = stack.pop()
        stack.append(_apply_binary_operator(token, left, right))

    if len(stack) != 1:
        raise CalculatorError("Некорректное выражение: лишние операнды.")

    return stack[0]


def calculate(expression: str) -> Number:
    """Convert an infix expression to RPN and calculate its result."""
    return evaluate_rpn(infix_to_rpn(expression))


def _apply_binary_operator(operator: str, left: Number, right: Number) -> Number:
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise CalculatorError("Деление на ноль невозможно.")
        return left / right
    if operator == "%":
        if right == 0:
            raise CalculatorError("Деление на ноль невозможно.")
        return left % right
    if operator == "^":
        return _integer_power(left, right)
    raise CalculatorError(f"Неизвестный оператор: '{operator}'.")


def _integer_power(base: Number, exponent: Number) -> Number:
    """Calculate an integer power by repeated squaring, without ** or pow()."""
    if isinstance(exponent, float) and not exponent.is_integer():
        raise CalculatorError("Показатель степени должен быть целым числом.")

    integer_exponent = int(exponent)
    if integer_exponent < 0 and base == 0:
        raise CalculatorError("Ноль нельзя возводить в отрицательную степень.")

    remaining = abs(integer_exponent)
    factor: Number = base
    result: Number = 1

    while remaining > 0:
        if remaining % 2 == 1:
            result *= factor
        factor *= factor
        remaining //= 2

    if integer_exponent < 0:
        return 1 / result
    return result


def _is_number(token: str) -> bool:
    """Return True when token has the calculator's decimal-number format."""
    if not token:
        return False

    dot_count = 0
    digit_count = 0
    for character in token:
        if "0" <= character <= "9":
            digit_count += 1
        elif character == ".":
            dot_count += 1
        else:
            return False

    return digit_count > 0 and dot_count <= 1


def _parse_number(token: str) -> Number:
    if "." in token:
        return float(token)
    return int(token)


def _format_result(result: Number) -> str:
    if isinstance(result, float) and result.is_integer():
        return str(int(result))
    return str(result)


def main() -> None:
    """Run the calculator in an interactive terminal session."""
    print("Калькулятор на основе обратной польской записи")
    print("Операции: +, -, *, /, %, ^. Для выхода введите exit.\n")

    while True:
        try:
            expression = input("Введите выражение: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nРабота калькулятора завершена.")
            break

        if expression.lower() in {"exit", "quit", "выход"}:
            print("Работа калькулятора завершена.")
            break

        try:
            rpn = infix_to_rpn(expression)
            result = evaluate_rpn(rpn)
            print(f"ОПЗ: {' '.join(rpn)}")
            print(f"Результат: {_format_result(result)}\n")
        except (CalculatorError, OverflowError) as error:
            print(f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()

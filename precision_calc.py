
from core.truncation import TruncationLevel, Truncated

def sign(x:int):
    if x == 0:
        return 0
    return -1 if x < 0 else 1



class PrecisionCalculator():
    def truncate(self, x: int, level: int):
        
        match level:
            case TruncationLevel.MINUS_TWO: truncated_val = sign(x)
            case TruncationLevel.MINUS_ONE: truncated_val = int(x)
            case TruncationLevel.ZERO: truncated_val = round(x, 1)
            case TruncationLevel.ONE: truncated_val = round(x, 2)
            case TruncationLevel.TWO: truncated_val = round(x, 3)

        return Truncated(truncated_val, level)


def test_precision_calc():
    # Ожидаемый результат:
    calc = PrecisionCalculator()

    number = 3.14159
    result1 = calc.truncate(number, TruncationLevel.MINUS_TWO) 
    assert result1.value == 1

    result2 = calc.truncate(number, TruncationLevel.MINUS_ONE)
    assert result2.value == 3

    result3 = calc.truncate(number, TruncationLevel.ZERO)
    assert result3.value == 3.1

    result4 = calc.truncate(number, TruncationLevel.ONE)
    assert result4.value == 3.14, result4.value

    result5 = calc.truncate(number, TruncationLevel.ONE)
    assert result5.value == 3.14, result5.value


if __name__ == "__main__":
    test_precision_calc()

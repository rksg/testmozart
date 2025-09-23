import pytest
from sample_code import Calculator, greet

def test_add_method_with_two_positive_integers():
    """
    SCENARIO: Test the 'add' method with two positive integers.
    EXPECTED: The method should return the correct sum of the two integers.
    """
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

def test_add_method_with_two_negative_integers():
    """
    SCENARIO: Test the 'add' method with two negative integers.
    EXPECTED: The method should return the correct sum of the two integers.
    """
    calc = Calculator()
    result = calc.add(-2, -3)
    assert result == -5

def test_add_method_with_positive_and_negative_integer():
    """
    SCENARIO: Test the 'add' method with a positive integer and a negative integer.
    EXPECTED: The method should return the correct result of the addition.
    """
    calc = Calculator()
    result = calc.add(5, -3)
    assert result == 2

def test_add_method_with_positive_integer_and_zero():
    """
    SCENARIO: Test the 'add' method with a positive integer and zero.
    EXPECTED: The method should return the positive integer itself.
    """
    calc = Calculator()
    result = calc.add(7, 0)
    assert result == 7

def test_add_method_with_two_zeros():
    """
    SCENARIO: Test the 'add' method with two zeros.
    EXPECTED: The method should return 0.
    """
    calc = Calculator()
    result = calc.add(0, 0)
    assert result == 0

def test_add_method_with_large_positive_integers():
    """
    SCENARIO: Test the 'add' method with very large positive integers.
    EXPECTED: The method should return the correct sum without overflow errors.
    """
    calc = Calculator()
    result = calc.add(999999999, 1000000000)
    assert result == 1999999999

def test_add_method_with_float_and_integer():
    """
    SCENARIO: Test the 'add' method with a float and an integer.
    EXPECTED: The method should return a float result (Python's actual behavior).
    """
    calc = Calculator()
    result = calc.add(2.5, 3)
    assert result == 5.5
    assert isinstance(result, float)

def test_add_method_with_string_and_integer_raises_error():
    """
    SCENARIO: Test the 'add' method with a string and an integer.
    EXPECTED: The method should raise a TypeError, as it expects two integers.
    """
    calc = Calculator()
    with pytest.raises(TypeError):
        calc.add("hello", 3)

def test_greet_function_with_typical_name():
    """
    SCENARIO: Test the 'greet' function with a typical name.
    EXPECTED: The function should return 'Hello, ' followed by the provided name.
    """
    result = greet("Alice")
    assert result == "Hello, Alice"

def test_greet_function_with_empty_string():
    """
    SCENARIO: Test the 'greet' function with an empty string.
    EXPECTED: The function should return 'Hello, '.
    """
    result = greet("")
    assert result == "Hello, "

def test_greet_function_with_name_containing_spaces():
    """
    SCENARIO: Test the 'greet' function with a name containing spaces.
    EXPECTED: The function should return 'Hello, ' followed by the name with spaces.
    """
    result = greet("John Doe")
    assert result == "Hello, John Doe"

def test_greet_function_with_very_long_string():
    """
    SCENARIO: Test the 'greet' function with a very long string.
    EXPECTED: The function should return 'Hello, ' followed by the complete long string.
    """
    long_name = "a" * 1000
    result = greet(long_name)
    assert result == f"Hello, {long_name}"

def test_greet_function_with_integer_input():
    """
    SCENARIO: Test the 'greet' function with an integer as input.
    EXPECTED: The function converts integer to string (Python's actual behavior).
    """
    result = greet(123)
    assert result == "Hello, 123"

def test_greet_function_with_none_input():
    """
    SCENARIO: Test the 'greet' function with None as input.
    EXPECTED: The function converts None to string (Python's actual behavior).
    """
    result = greet(None)
    assert result == "Hello, None"

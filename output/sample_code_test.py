import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sample_code import Calculator, StringProcessor, greet, factorial, find_max, is_palindrome

def test_the_greet_function_with_typical_inputs():
    """
    Tests: Test the 'greet' function with typical inputs
    Expected Outcome: Should return a greeting message
    """
    assert greet("World") == "Hello, World!"

def test_the_greet_function_with_edge_case_inputs():
    """
    Tests: Test the 'greet' function with edge case inputs
    Expected Outcome: Should return a greeting message for an empty name
    """
    assert greet("") == "Hello, stranger!"

def test_the_factorial_function_with_typical_inputs():
    """
    Tests: Test the 'factorial' function with typical inputs
    Expected Outcome: Should return the correct factorial value
    """
    assert factorial(5) == 120

def test_the_factorial_function_with_edge_case_inputs():
    """
    Tests: Test the 'factorial' function with edge case inputs
    Expected Outcome: Should handle zero, one, and negative inputs correctly
    """
    assert factorial(0) == 1
    assert factorial(1) == 1
    with pytest.raises(ValueError):
        factorial(-1)

def test_the_find_max_function_with_typical_inputs():
    """
    Tests: Test the 'find_max' function with typical inputs
    Expected Outcome: Should return the maximum value from a list
    """
    assert find_max([1, 5, 2, 9, 3]) == 9

def test_the_find_max_function_with_edge_case_inputs():
    """
    Tests: Test the 'find_max' function with edge case inputs
    Expected Outcome: Should raise an error for an empty or invalid list
    """
    with pytest.raises(ValueError):
        find_max([])
    with pytest.raises(TypeError):
        find_max([1, "a", 3])

def test_the_is_palindrome_function_with_typical_inputs():
    """
    Tests: Test the 'is_palindrome' function with typical inputs
    Expected Outcome: Should correctly identify a palindrome
    """
    assert is_palindrome("radar") is True
    assert is_palindrome("hello") is False

def test_the_is_palindrome_function_with_edge_case_inputs():
    """
    Tests: Test the 'is_palindrome' function with edge case inputs
    Expected Outcome: Should handle non-string inputs, case, and spacing
    """
    assert is_palindrome("A man a plan a canal Panama") is True
    with pytest.raises(TypeError):
        is_palindrome(121)

def test_the_add_method_of_calculator_class():
    """
    Tests: Test the 'add' method of 'Calculator' class
    Expected Outcome: Should return the sum of two numbers
    """
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_the_subtract_method_of_calculator_class():
    """
    Tests: Test the 'subtract' method of 'Calculator' class
    Expected Outcome: Should return the difference of two numbers
    """
    calc = Calculator()
    assert calc.subtract(5, 3) == 2

def test_the_multiply_method_of_calculator_class():
    """
    Tests: Test the 'multiply' method of 'Calculator' class
    Expected Outcome: Should return the product of two numbers
    """
    calc = Calculator()
    assert calc.multiply(4, 3) == 12

def test_the_divide_method_of_calculator_class():
    """
    Tests: Test the 'divide' method of 'Calculator' class
    Expected Outcome: Should return the quotient and handle division by zero
    """
    calc = Calculator()
    assert calc.divide(10, 2) == 5.0
    with pytest.raises(ValueError):
        calc.divide(5, 0)

def test_the_power_method_of_calculator_class():
    """
    Tests: Test the 'power' method of 'Calculator' class
    Expected Outcome: Should return the result of the power operation and handle negative exponents
    """
    calc = Calculator()
    assert calc.power(2, 3) == 8
    with pytest.raises(ValueError):
        calc.power(2, -1)

def test_the_reverse_string_method_of_stringprocessor_class():
    """
    Tests: Test the 'reverse_string' method of 'StringProcessor' class
    Expected Outcome: Should return the reversed string and handle non-string input
    """
    sp = StringProcessor()
    assert sp.reverse_string("hello") == "olleh"
    with pytest.raises(TypeError):
        sp.reverse_string(123)

def test_the_count_words_method_of_stringprocessor_class():
    """
    Tests: Test the 'count_words' method of 'StringProcessor' class
    Expected Outcome: Should return the correct word count for typical and empty strings
    """
    sp = StringProcessor()
    assert sp.count_words("hello world") == 2
    assert sp.count_words("") == 0

def test_the_capitalize_words_method_of_stringprocessor_class():
    """
    Tests: Test the 'capitalize_words' method of 'StringProcessor' class
    Expected Outcome: Should return a string with each word capitalized
    """
    sp = StringProcessor()
    assert sp.capitalize_words("hello world") == "Hello World"

def test_instantiation_and_basic_usage_of_calculator_class():
    """
    Tests: Test instantiation and basic usage of 'Calculator' class
    Expected Outcome: Should create a valid instance of the Calculator class
    """
    calc = Calculator()
    assert isinstance(calc, Calculator)

def test_instantiation_and_basic_usage_of_stringprocessor_class():
    """
    Tests: Test instantiation and basic usage of 'StringProcessor' class
    Expected Outcome: Should create a valid instance of the StringProcessor class
    """
    sp = StringProcessor()
    assert isinstance(sp, StringProcessor)
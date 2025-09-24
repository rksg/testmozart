import pytest
from sample_code import Calculator, StringProcessor, greet, factorial, find_max, is_palindrome
def test_the_add_method_of_the_calculator_class_with_two_positive_integers_5_3():
    """
    Tests: Test the 'add' method of the Calculator class with two positive integers (5, 3).
    Expected Outcome: The method should return 8.
    """
    calculator = Calculator()
    result = calculator.add(5, 3)
    assert result == 8
def test_the_add_method_of_the_calculator_class_with_a_positive_and_a_negative_integer_10_3():
    """
    Tests: Test the 'add' method of the Calculator class with a positive and a negative integer (10, -3).
    Expected Outcome: The method should return 7.
    """
    calculator = Calculator()
    result = calculator.add(10, -3)
    assert result == 7
def test_the_subtract_method_of_the_calculator_class_where_the_first_number_is_larger_10_3():
    """
    Tests: Test the 'subtract' method of the Calculator class where the first number is larger (10, 3).
    Expected Outcome: The method should return 7.
    """
    calculator = Calculator()
    result = calculator.subtract(10, 3)
    assert result == 7
def test_the_subtract_method_of_the_calculator_class_where_the_second_number_is_larger_3_10():
    """
    Tests: Test the 'subtract' method of the Calculator class where the second number is larger (3, 10).
    Expected Outcome: The method should return -7.
    """
    calculator = Calculator()
    result = calculator.subtract(3, 10)
    assert result == -7
def test_the_multiply_method_of_the_calculator_class_with_two_positive_integers_4_5():
    """
    Tests: Test the 'multiply' method of the Calculator class with two positive integers (4, 5).
    Expected Outcome: The method should return 20.
    """
    calculator = Calculator()
    result = calculator.multiply(4, 5)
    assert result == 20
def test_the_multiply_method_of_the_calculator_class_with_a_positive_and_a_negative_integer_4_5():
    """
    Tests: Test the 'multiply' method of the Calculator class with a positive and a negative integer (4, -5).
    Expected Outcome: The method should return -20.
    """
    calculator = Calculator()
    result = calculator.multiply(4, -5)
    assert result == -20
def test_the_multiply_method_of_the_calculator_class_with_zero_10_0():
    """
    Tests: Test the 'multiply' method of the Calculator class with zero (10, 0).
    Expected Outcome: The method should return 0.
    """
    calculator = Calculator()
    result = calculator.multiply(10, 0)
    assert result == 0
def test_the_divide_method_of_the_calculator_class_with_valid_integers_10_2():
    """
    Tests: Test the 'divide' method of the Calculator class with valid integers (10, 2).
    Expected Outcome: The method should return 5.0.
    """
    calculator = Calculator()
    result = calculator.divide(10, 2)
    assert result == 5.0
def test_the_divide_method_of_the_calculator_class_to_produce_a_float_result_5_2():
    """
    Tests: Test the 'divide' method of the Calculator class to produce a float result (5, 2).
    Expected Outcome: The method should return 2.5.
    """
    calculator = Calculator()
    result = calculator.divide(5, 2)
    assert result == 2.5
def test_the_divide_method_of_the_calculator_class_with_division_by_zero_10_0():
    """
    Tests: Test the 'divide' method of the Calculator class with division by zero (10, 0).
    Expected Outcome: The method should raise a ValueError with the message "Cannot divide by zero".
    """
    calculator = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(10, 0)
def test_the_power_method_of_the_calculator_class_with_a_positive_exponent_2_3():
    """
    Tests: Test the 'power' method of the Calculator class with a positive exponent (2, 3).
    Expected Outcome: The method should return 8.
    """
    calculator = Calculator()
    result = calculator.power(2, 3)
    assert result == 8
def test_the_power_method_of_the_calculator_class_with_an_exponent_of_zero_10_0():
    """
    Tests: Test the 'power' method of the Calculator class with an exponent of zero (10, 0).
    Expected Outcome: The method should return 1.
    """
    calculator = Calculator()
    result = calculator.power(10, 0)
    assert result == 1
def test_the_power_method_of_the_calculator_class_with_a_negative_exponent_2_1():
    """
    Tests: Test the 'power' method of the Calculator class with a negative exponent (2, -1).
    Expected Outcome: The method should raise a ValueError with the message "Negative exponents not supported".
    """
    calculator = Calculator()
    with pytest.raises(ValueError, match="Negative exponents not supported"):
        calculator.power(2, -1)
def test_the_reverse_string_method_of_the_stringprocessor_class_with_a_simple_string_hello():
    """
    Tests: Test the 'reverse_string' method of the StringProcessor class with a simple string ("hello").
    Expected Outcome: The method should return "olleh".
    """
    string_processor = StringProcessor()
    result = string_processor.reverse_string("hello")
    assert result == "olleh"
def test_the_reverse_string_method_of_the_stringprocessor_class_with_an_empty_string():
    """
    Tests: Test the 'reverse_string' method of the StringProcessor class with an empty string.
    Expected Outcome: The method should return an empty string.
    """
    string_processor = StringProcessor()
    result = string_processor.reverse_string("")
    assert result == ""
def test_the_reverse_string_method_of_the_stringprocessor_class_with_a_nonstring_input_eg_an_integer():
    """
    Tests: Test the 'reverse_string' method of the StringProcessor class with a non-string input (e.g., an integer).
    Expected Outcome: The method should raise a TypeError.
    """
    string_processor = StringProcessor()
    with pytest.raises(TypeError):
        string_processor.reverse_string(123)
def test_the_count_words_method_of_the_stringprocessor_class_with_a_typical_sentence():
    """
    Tests: Test the 'count_words' method of the StringProcessor class with a typical sentence.
    Expected Outcome: The method should return the correct number of words.
    """
    string_processor = StringProcessor()
    result = string_processor.count_words("This is a typical sentence.")
    assert result == 5
def test_the_count_words_method_of_the_stringprocessor_class_with_an_empty_string():
    """
    Tests: Test the 'count_words' method of the StringProcessor class with an empty string.
    Expected Outcome: The method should return 0.
    """
    string_processor = StringProcessor()
    result = string_processor.count_words("")
    assert result == 0
def test_the_count_words_method_of_the_stringprocessor_class_with_a_string_containing_multiple_spaces_between_words():
    """
    Tests: Test the 'count_words' method of the StringProcessor class with a string containing multiple spaces between words.
    Expected Outcome: The method should handle multiple spaces correctly and return the right word count.
    """
    string_processor = StringProcessor()
    result = string_processor.count_words("a  b   c")
    assert result == 3
def test_the_capitalize_words_method_of_the_stringprocessor_class_with_a_lowercase_sentence():
    """
    Tests: Test the 'capitalize_words' method of the StringProcessor class with a lowercase sentence.
    Expected Outcome: The method should return the sentence with the first letter of each word capitalized.
    """
    string_processor = StringProcessor()
    result = string_processor.capitalize_words("a lowercase sentence")
    assert result == "A Lowercase Sentence"
def test_the_capitalize_words_method_of_the_stringprocessor_class_with_an_already_capitalized_sentence():
    """
    Tests: Test the 'capitalize_words' method of the StringProcessor class with an already capitalized sentence.
    Expected Outcome: The method should return the sentence unchanged.
    """
    string_processor = StringProcessor()
    result = string_processor.capitalize_words("Already Capitalized Sentence")
    assert result == "Already Capitalized Sentence"
def test_the_greet_function_with_a_valid_name_alice():
    """
    Tests: Test the 'greet' function with a valid name ("Alice").
    Expected Outcome: The function should return "Hello, Alice!".
    """
    result = greet("Alice")
    assert result == "Hello, Alice!"
def test_the_greet_function_with_an_empty_string():
    """
    Tests: Test the 'greet' function with an empty string.
    Expected Outcome: The function should return "Hello, stranger!".
    """
    result = greet("")
    assert result == "Hello, stranger!"
def test_the_factorial_function_with_a_positive_integer_5():
    """
    Tests: Test the 'factorial' function with a positive integer (5).
    Expected Outcome: The function should return 120.
    """
    result = factorial(5)
    assert result == 120
def test_the_factorial_function_with_zero():
    """
    Tests: Test the 'factorial' function with zero.
    Expected Outcome: The function should return 1.
    """
    result = factorial(0)
    assert result == 1
def test_the_factorial_function_with_a_negative_number():
    """
    Tests: Test the 'factorial' function with a negative number.
    Expected Outcome: The function should raise a ValueError.
    """
    with pytest.raises(ValueError):
        factorial(-1)
def test_the_find_max_function_with_a_list_of_positive_integers():
    """
    Tests: Test the 'find_max' function with a list of positive integers.
    Expected Outcome: The function should return the largest number in the list.
    """
    result = find_max([1, 2, 3, 4, 5])
    assert result == 5
def test_the_find_max_function_with_a_list_containing_negative_numbers_and_zero():
    """
    Tests: Test the 'find_max' function with a list containing negative numbers and zero.
    Expected Outcome: The function should return 0.
    """
    result = find_max([-1, -2, 0])
    assert result == 0
def test_the_find_max_function_with_an_empty_list():
    """
    Tests: Test the 'find_max' function with an empty list.
    Expected Outcome: The function should raise a ValueError.
    """
    with pytest.raises(ValueError):
        find_max([])
def test_the_find_max_function_with_a_list_containing_nonnumeric_types():
    """
    Tests: Test the 'find_max' function with a list containing non-numeric types.
    Expected Outcome: The function should raise a TypeError.
    """
    with pytest.raises(TypeError):
        find_max([1, "a"])
def test_the_is_palindrome_function_with_a_palindromic_string_madam():
    """
    Tests: Test the 'is_palindrome' function with a palindromic string ("madam").
    Expected Outcome: The function should return True.
    """
    result = is_palindrome("madam")
    assert result is True
def test_the_is_palindrome_function_with_a_nonpalindromic_string_hello():
    """
    Tests: Test the 'is_palindrome' function with a non-palindromic string ("hello").
    Expected Outcome: The function should return False.
    """
    result = is_palindrome("hello")
    assert result is False
def test_the_is_palindrome_function_with_a_complex_palindromic_sentence_a_man_a_plan_a_canal_panama():
    """
    Tests: Test the 'is_palindrome' function with a complex palindromic sentence ("A man a plan a canal Panama").
    Expected Outcome: The function should return True, ignoring case and spaces.
    """
    result = is_palindrome("A man a plan a canal Panama")
    assert result is True
def test_the_is_palindrome_function_with_a_nonstring_input():
    """
    Tests: Test the 'is_palindrome' function with a non-string input.
    Expected Outcome: The function should raise a TypeError.
    """
    with pytest.raises(TypeError):
        is_palindrome(121)

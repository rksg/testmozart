import pytest
from sample_code import sum_even_numbers

def test_the_sum_even_numbers_function_with_a_list_containing_even_and_odd_numbers():
    """
    Tests: Test the `sum_even_numbers` function with a list containing even and odd numbers.
    Expected Outcome: The function should return the sum of only the even numbers in the list.
    """
    numbers = [1, 2, 3, 4, 5, 6]
    result = sum_even_numbers(numbers)
    assert result == 12

def test_the_sum_even_numbers_function_with_a_list_containing_only_odd_numbers():
    """
    Tests: Test the `sum_even_numbers` function with a list containing only odd numbers.
    Expected Outcome: The function should return 0, as there are no even numbers to sum.
    """
    numbers = [1, 3, 5, 7, 9]
    result = sum_even_numbers(numbers)
    assert result == 0

def test_the_sum_even_numbers_function_with_an_empty_list():
    """
    Tests: Test the `sum_even_numbers` function with an empty list.
    Expected Outcome: The function should return 0, as there are no numbers to sum.
    """
    numbers = []
    result = sum_even_numbers(numbers)
    assert result == 0
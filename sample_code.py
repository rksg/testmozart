"""A sample module for demonstration and testing."""
class Calculator:
    """A simple calculator class with various mathematical operations."""
    def add(self, a: int, b: int) -> int:
        """Adds two numbers together."""
        return a + b
    def subtract(self, a: int, b: int) -> int:
        """Subtracts the second number from the first."""
        return a - b
    def multiply(self, a: int, b: int) -> int:
        """Multiplies two numbers together."""
        return a * b
    def divide(self, a: int, b: int) -> float:
        """Divides the first number by the second."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    def power(self, base: int, exponent: int) -> int:
        """Raises base to the power of exponent."""
        if exponent < 0:
            raise ValueError("Negative exponents not supported")
        return base ** exponent
class StringProcessor:
    """A class for processing strings."""
    def reverse_string(self, text: str) -> str:
        """Reverses the input string."""
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        return text[::-1]
    def count_words(self, text: str) -> int:
        """Counts the number of words in the text."""
        if not text:
            return 0
        return len(text.split())
    def capitalize_words(self, text: str) -> str:
        """Capitalizes the first letter of each word."""
        return text.title()
def greet(name: str) -> str:
    """Returns a greeting message."""
    if not name:
        return "Hello, stranger!"
    return f"Hello, {name}!"
def factorial(n: int) -> int:
    """Calculates the factorial of a number."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
def find_max(numbers: list) -> int:
    """Finds the maximum number in a list."""
    if not numbers:
        raise ValueError("Cannot find max of empty list")
    if not all(isinstance(x, (int, float)) for x in numbers):
        raise TypeError("All elements must be numbers")
    return max(numbers)
def is_palindrome(text: str) -> bool:
    """Checks if a string is a palindrome."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

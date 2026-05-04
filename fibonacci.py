def fibonacci_series(n: int) -> list:
    if n == 0:
        return []
    elif n == 1:
        return [0]
    fib_series = [0, 1]
    for i in range(2, n):
        fib_series.append(fib_series[-1] + fib_series[-2])
    return fib_series[:n]

# Test cases
def test_fibonacci():
    assert fibonacci_series(0) == [], "Test with n=0 failed"
    assert fibonacci_series(1) == [0], "Test with n=1 failed"
    assert fibonacci_series(5) == [0, 1, 1, 2, 3], "Test with n=5 failed"
    assert fibonacci_series(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34], "Test with n=10 failed"

test_fibonacci()


def _fibonacci_series(n: int):
	series = []
	a, b = 0, 1
	for _ in range(n):
		series.append(a)
		a, b = b, a + b
	return series


def test_fibonacci_series_first_ten_numbers():
	assert _fibonacci_series(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_fibonacci_series_edge_cases():
	assert _fibonacci_series(0) == []
	assert _fibonacci_series(1) == [0]

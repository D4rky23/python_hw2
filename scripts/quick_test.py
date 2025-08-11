"""Quick test script to verify the API is working."""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_power():
    """Test power calculation."""
    payload = {"base": 2, "exponent": 3}
    response = requests.post(f"{BASE_URL}/api/v1/power/", json=payload)
    print(f"\nPower calculation: {response.status_code}")
    print(f"Request: {payload}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_fibonacci():
    """Test Fibonacci calculation."""
    response = requests.get(f"{BASE_URL}/api/v1/fibonacci/5")
    print(f"\nFibonacci calculation: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_factorial():
    """Test factorial calculation."""
    payload = {"n": 5}
    response = requests.post(f"{BASE_URL}/api/v1/factorial/", json=payload)
    print(f"\nFactorial calculation: {response.status_code}")
    print(f"Request: {payload}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_metrics():
    """Test metrics endpoint."""
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"\nMetrics endpoint: {response.status_code}")
    print(f"Content length: {len(response.text)} characters")
    return response.status_code == 200


if __name__ == "__main__":
    print("🧪 Testing Math Service API")
    print("=" * 50)

    try:
        tests = [
            ("Health Check", test_health),
            ("Power Calculation", test_power),
            ("Fibonacci Calculation", test_fibonacci),
            ("Factorial Calculation", test_factorial),
            ("Metrics Endpoint", test_metrics),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, "PASS" if success else "FAIL"))
            except Exception as e:
                results.append((test_name, f"ERROR: {e}"))
            print()

        print("=" * 50)
        print("Test Results:")
        for test_name, result in results:
            print(f"{test_name}: {result}")

        all_passed = all("PASS" in result for _, result in results)
        print(
            f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}"
        )

    except Exception as e:
        print(f"Failed to run tests: {e}")

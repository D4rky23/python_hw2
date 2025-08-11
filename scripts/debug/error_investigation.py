#!/usr/bin/env python3
"""Detailed Error Investigation for Math Service API"""

import httpx
import json

BASE_URL = "http://localhost:8000"


def investigate_fibonacci_errors():
    """Investigate Fibonacci 500 errors"""
    print("=== FIBONACCI ERROR INVESTIGATION ===")

    test_cases = [0, 1, 5, 15]

    for n in test_cases:
        try:
            response = httpx.get(f"{BASE_URL}/api/v1/fibonacci/{n}")
            print(f"\nFibonacci({n}):")
            print(f"Status: {response.status_code}")

            if response.status_code != 200:
                print(f"Headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")

                # Try to parse as JSON for error details
                try:
                    error_json = response.json()
                    print(f"Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    print("Could not parse response as JSON")
            else:
                print(f"Success: {response.json()}")

        except Exception as e:
            print(f"Exception testing Fibonacci({n}): {e}")


def investigate_power_errors():
    """Investigate Power 500 errors"""
    print("\n=== POWER ERROR INVESTIGATION ===")

    test_cases = [
        {"base": 2, "exponent": 3},  # This one worked
        {"base": 5, "exponent": 2},  # This failed
        {"base": 10, "exponent": 0},  # This failed
        {"base": 3, "exponent": 4},  # This failed
    ]

    for case in test_cases:
        try:
            response = httpx.post(f"{BASE_URL}/api/v1/power/", json=case)
            print(f"\nPower({case['base']}^{case['exponent']}):")
            print(f"Status: {response.status_code}")

            if response.status_code != 200:
                print(f"Headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")

                try:
                    error_json = response.json()
                    print(f"Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    print("Could not parse response as JSON")
            else:
                print(f"Success: {response.json()}")

        except Exception as e:
            print(
                f"Exception testing Power({case['base']}^{case['exponent']}): {e}"
            )


def investigate_factorial_errors():
    """Investigate Factorial 500 errors"""
    print("\n=== FACTORIAL ERROR INVESTIGATION ===")

    test_cases = [0, 1, 5, 10]  # 5 worked, others failed

    for n in test_cases:
        try:
            response = httpx.post(
                f"{BASE_URL}/api/v1/factorial/", json={"n": n}
            )
            print(f"\nFactorial({n}):")
            print(f"Status: {response.status_code}")

            if response.status_code != 200:
                print(f"Headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")

                try:
                    error_json = response.json()
                    print(f"Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    print("Could not parse response as JSON")
            else:
                print(f"Success: {response.json()}")

        except Exception as e:
            print(f"Exception testing Factorial({n}): {e}")


def test_authorization():
    """Test if API key is required"""
    print("\n=== AUTHORIZATION TESTING ===")

    # Test without any authorization
    response = httpx.get(f"{BASE_URL}/api/v1/fibonacci/5")
    print(f"No auth - Fibonacci(5): {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")

    # Test with some dummy API key
    headers = {"X-API-Key": "test-key"}
    response = httpx.get(f"{BASE_URL}/api/v1/fibonacci/5", headers=headers)
    print(f"With dummy API key - Fibonacci(5): {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")


if __name__ == "__main__":
    print("Starting Detailed Error Investigation")
    print("=" * 50)

    investigate_fibonacci_errors()
    investigate_power_errors()
    investigate_factorial_errors()
    test_authorization()

    print("\nError Investigation Complete!")

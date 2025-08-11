#!/usr/bin/env python3
"""QA Test Suite for Math Service API"""

import httpx
import json
import asyncio
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_health_endpoint():
    """Test the health check endpoint"""
    print("=== HEALTH ENDPOINT TEST ===")
    try:
        response = httpx.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Assertions
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] == "healthy"
        assert json_response["service"] == "math-service"
        print("✅ Health endpoint test PASSED")

    except Exception as e:
        print(f"❌ Health endpoint test FAILED: {e}")
    print()


def test_metrics_endpoint():
    """Test the metrics endpoint"""
    print("=== METRICS ENDPOINT TEST ===")
    try:
        response = httpx.get(f"{BASE_URL}/metrics")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Response Length: {len(response.text)} characters")
        print("First 500 characters:")
        print(response.text[:500])
        print("...")

        # Assertions
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        print("✅ Metrics endpoint test PASSED")

    except Exception as e:
        print(f"❌ Metrics endpoint test FAILED: {e}")
    print()


def test_fibonacci_endpoint():
    """Test the Fibonacci endpoint"""
    print("=== FIBONACCI ENDPOINT TEST ===")
    try:
        # Test valid cases
        test_cases = [0, 1, 5, 10, 15]

        for n in test_cases:
            response = httpx.get(f"{BASE_URL}/api/v1/fibonacci/{n}")
            print(f"Fibonacci({n}): Status {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Result: {result}")

                # Basic assertions
                assert result["n"] == n
                assert "result" in result

        print("✅ Fibonacci endpoint test PASSED")

    except Exception as e:
        print(f"❌ Fibonacci endpoint test FAILED: {e}")
    print()


def test_power_endpoint():
    """Test the Power endpoint"""
    print("=== POWER ENDPOINT TEST ===")
    try:
        # Test valid cases
        test_cases = [
            {"base": 2, "exponent": 3},
            {"base": 5, "exponent": 2},
            {"base": 10, "exponent": 0},
            {"base": 3, "exponent": 4},
        ]

        for case in test_cases:
            response = httpx.post(f"{BASE_URL}/api/v1/power/", json=case)
            print(
                f"Power({case['base']}^{case['exponent']}): Status {response.status_code}"
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  Result: {result}")

                # Basic assertions
                assert result["base"] == case["base"]
                assert result["exponent"] == case["exponent"]
                assert "result" in result

        print("✅ Power endpoint test PASSED")

    except Exception as e:
        print(f"❌ Power endpoint test FAILED: {e}")
    print()


def test_factorial_endpoint():
    """Test the Factorial endpoint"""
    print("=== FACTORIAL ENDPOINT TEST ===")
    try:
        # Test valid cases
        test_cases = [0, 1, 5, 10]

        for n in test_cases:
            response = httpx.post(
                f"{BASE_URL}/api/v1/factorial/", json={"n": n}
            )
            print(f"Factorial({n}): Status {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Result: {result}")

                # Basic assertions
                assert result["n"] == n
                assert "result" in result

        print("✅ Factorial endpoint test PASSED")

    except Exception as e:
        print(f"❌ Factorial endpoint test FAILED: {e}")
    print()


def test_edge_cases():
    """Test edge cases and error conditions"""
    print("=== EDGE CASES AND ERROR TESTING ===")

    # Test negative Fibonacci
    try:
        response = httpx.get(f"{BASE_URL}/api/v1/fibonacci/-1")
        print(f"Negative Fibonacci: Status {response.status_code}")
        assert response.status_code == 422  # Validation error
        print("✅ Negative Fibonacci validation PASSED")
    except Exception as e:
        print(f"❌ Negative Fibonacci test FAILED: {e}")

    # Test negative factorial
    try:
        response = httpx.post(f"{BASE_URL}/api/v1/factorial/", json={"n": -1})
        print(f"Negative Factorial: Status {response.status_code}")
        assert response.status_code == 422  # Validation error
        print("✅ Negative Factorial validation PASSED")
    except Exception as e:
        print(f"❌ Negative Factorial test FAILED: {e}")

    # Test negative exponent for power
    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/power/", json={"base": 2, "exponent": -1}
        )
        print(f"Negative Exponent: Status {response.status_code}")
        assert response.status_code == 422  # Validation error
        print("✅ Negative Exponent validation PASSED")
    except Exception as e:
        print(f"❌ Negative Exponent test FAILED: {e}")

    print()


def test_api_documentation():
    """Test API documentation endpoints"""
    print("=== API DOCUMENTATION TEST ===")

    # Test OpenAPI JSON
    try:
        response = httpx.get(f"{BASE_URL}/openapi.json")
        print(f"OpenAPI JSON: Status {response.status_code}")
        assert response.status_code == 200
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        print("✅ OpenAPI JSON test PASSED")
    except Exception as e:
        print(f"❌ OpenAPI JSON test FAILED: {e}")

    # Test Swagger UI
    try:
        response = httpx.get(f"{BASE_URL}/docs")
        print(f"Swagger UI: Status {response.status_code}")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        print("✅ Swagger UI test PASSED")
    except Exception as e:
        print(f"❌ Swagger UI test FAILED: {e}")

    # Test ReDoc
    try:
        response = httpx.get(f"{BASE_URL}/redoc")
        print(f"ReDoc: Status {response.status_code}")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        print("✅ ReDoc test PASSED")
    except Exception as e:
        print(f"❌ ReDoc test FAILED: {e}")

    print()


if __name__ == "__main__":
    print("🚀 Starting QA Testing for Math Service API")
    print("=" * 50)

    # Run all tests
    test_health_endpoint()
    test_metrics_endpoint()
    test_fibonacci_endpoint()
    test_power_endpoint()
    test_factorial_endpoint()
    test_edge_cases()
    test_api_documentation()

    print("🏁 QA Testing Complete!")

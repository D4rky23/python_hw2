import requests


def test_calculation(base, exponent, expected_blocked=False):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/power/",
            json={"base": base, "exponent": exponent},
        )
        print(f"Testing: {base}^{exponent}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if expected_blocked:
            if response.status_code == 400:
                print("Correctly blocked by protection!")
            else:
                print("Should have been blocked but wasn't")
        else:
            if response.status_code == 200:
                print("Calculation succeeded as expected")
            else:
                print("Should have succeeded but was blocked")

        print("-" * 50)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None


print("=== TESTING OVERFLOW PROTECTION ===")

# Test 1: Should be blocked by "exponent > 50"
test_calculation(2, 51, expected_blocked=True)

# Test 2: Should be blocked by "base > 100 and exponent > 20"
test_calculation(150, 25, expected_blocked=True)

# Test 3: Should be blocked by "base > 10 and exponent > 100"
test_calculation(15, 101, expected_blocked=True)

# Test 4: Should work (within all limits)
test_calculation(2, 10, expected_blocked=False)

# Test 5: Should work (edge case)
test_calculation(10, 50, expected_blocked=False)

print("=== OVERFLOW PROTECTION TESTING COMPLETE ===")

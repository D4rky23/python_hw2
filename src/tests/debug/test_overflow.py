import requests


def test_power_calculation(base, exponent):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/power/",
            json={"base": base, "exponent": exponent},
        )
        print(f"Base: {base}, Exponent: {exponent}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print("-" * 50)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None


# Test cases to verify overflow protection
print("Testing overflow protection after cache clear...")

# This should be blocked by exponent > 50 protection
test_power_calculation(10, 51)

# This should be blocked by exponent > 50 protection
test_power_calculation(2, 55)

# This should work (within limits)
test_power_calculation(2, 10)

# This should be blocked by base > 100 and exponent > 20 protection
test_power_calculation(150, 25)

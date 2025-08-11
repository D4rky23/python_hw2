import requests


def test_single_calculation(base, exponent):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/power/",
            json={"base": base, "exponent": exponent},
        )
        print(f"Testing: {base}^{exponent}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 400:
            print("Correctly blocked by protection!")
        elif response.status_code == 200:
            print("Protection failed - calculation went through")
        else:
            print(f"Unexpected status code: {response.status_code}")

        print("-" * 50)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None


# Test with exponent=51 which should definitely be blocked by "exponent > 50" check
test_single_calculation(2, 51)

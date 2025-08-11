import requests


def test_fresh_case():
    # Use different parameters that haven't been calculated before
    base = 101  # Just over 100
    exponent = 21  # Just over 20

    print(f"Testing fresh case: {base}^{exponent}")
    print(f"base > 100: {base > 100}")
    print(f"exponent > 20: {exponent > 20}")
    print(f"Should be blocked: {base > 100 and exponent > 20}")

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/power/",
            json={"base": base, "exponent": exponent},
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 400:
            print("Correctly blocked!")
        else:
            print("Should have been blocked but wasn't")

    except Exception as e:
        print(f"Error: {e}")


test_fresh_case()

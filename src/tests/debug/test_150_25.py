import requests


def test_specific_case():
    base = 150
    exponent = 25

    print(f"Testing specific case: {base}^{exponent}")
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


test_specific_case()

import requests


def test_original_problem():
    # Test the original case that was causing 500 errors
    base = 999
    exponent = 100

    print(f"Testing original problem case: {base}^{exponent}")

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/power/",
            json={"base": base, "exponent": exponent},
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 400:
            print("✅ Correctly blocked by protection!")
        elif response.status_code == 200:
            print("⚠️ Calculation succeeded (might be acceptable)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


test_original_problem()

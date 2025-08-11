"""End-to-end test script for the Math Service API."""

import asyncio
import json
import time
from typing import Dict, Any

import httpx


class MathServiceTester:
    """Test client for the Math Service API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def test_health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint."""
        print("Testing health check...")
        response = await self.client.get("/health")
        result = response.json()
        print(f"Health check: {result}")
        assert response.status_code == 200
        assert result["status"] == "healthy"
        return result

    async def test_power_operation(self) -> Dict[str, Any]:
        """Test power calculation."""
        print("\nTesting power operation...")
        payload = {"base": 2, "exponent": 10}
        response = await self.client.post("/api/v1/power/", json=payload)
        result = response.json()
        print(f"Power 2^10 = {result['result']}")
        assert response.status_code == 200
        assert result["result"] == 1024
        return result

    async def test_fibonacci_operation(self) -> Dict[str, Any]:
        """Test Fibonacci calculation."""
        print("\nTesting Fibonacci operation...")
        response = await self.client.get("/api/v1/fibonacci/15")
        result = response.json()
        print(f"Fibonacci(15) = {result['result']}")
        assert response.status_code == 200
        assert result["result"] == 610  # 15th Fibonacci number
        return result

    async def test_factorial_operation(self) -> Dict[str, Any]:
        """Test factorial calculation."""
        print("\nTesting factorial operation...")
        payload = {"n": 10}
        response = await self.client.post("/api/v1/factorial/", json=payload)
        result = response.json()
        print(f"10! = {result['result']}")
        assert response.status_code == 200
        assert result["result"] == 3628800  # 10!
        return result

    async def test_error_handling(self) -> None:
        """Test error handling."""
        print("\nTesting error handling...")

        # Test negative exponent
        response = await self.client.post(
            "/api/v1/power/", json={"base": 2, "exponent": -1}
        )
        print(f"Negative exponent error: {response.status_code}")
        assert response.status_code == 422

        # Test negative factorial
        response = await self.client.post("/api/v1/factorial/", json={"n": -1})
        print(f"Negative factorial error: {response.status_code}")
        assert response.status_code == 422

    async def test_metrics_endpoint(self) -> str:
        """Test metrics endpoint."""
        print("\nTesting metrics endpoint...")
        response = await self.client.get("/metrics")
        metrics = response.text
        print(f"Metrics available: {len(metrics)} characters")
        assert response.status_code == 200
        assert "http_requests_total" in metrics
        return metrics

    async def load_test(self, operations: int = 10) -> None:
        """Perform a simple load test."""
        print(f"\nPerforming load test with {operations} operations...")

        start_time = time.time()
        tasks = []

        for i in range(operations):
            # Mix of different operations
            if i % 3 == 0:
                task = self.client.post(
                    "/api/v1/power/", json={"base": 2, "exponent": i % 10}
                )
            elif i % 3 == 1:
                task = self.client.get(f"/api/v1/fibonacci/{i % 20}")
            else:
                task = self.client.post(
                    "/api/v1/factorial/", json={"n": i % 10}
                )

            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        success_count = sum(1 for r in responses if r.status_code == 200)
        print(
            f"Load test completed: {success_count}/{operations} successful in {duration:.2f}s"
        )
        print(f"Average response time: {duration/operations:.3f}s per request")

    async def run_all_tests(self) -> None:
        """Run all tests."""
        print("=" * 60)
        print("Math Service API End-to-End Test")
        print("=" * 60)

        try:
            await self.test_health_check()
            await self.test_power_operation()
            await self.test_fibonacci_operation()
            await self.test_factorial_operation()
            await self.test_error_handling()
            await self.test_metrics_endpoint()
            await self.load_test()

            print("\n" + "=" * 60)
            print("All tests passed successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\nTest failed: {e}")
            raise
        finally:
            await self.client.aclose()


async def main():
    """Main test function."""
    tester = MathServiceTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

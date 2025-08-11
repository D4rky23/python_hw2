"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app


class TestPowerAPI:
    """Integration tests for power endpoints."""
    
    def test_calculate_power_success(self):
        """Test successful power calculation via API."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/power/",
                json={"base": 2, "exponent": 3}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["base"] == 2
            assert data["exponent"] == 3
            assert data["result"] == 8
    
    def test_calculate_power_validation_error(self):
        """Test power calculation with invalid input."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/power/",
                json={"base": 2, "exponent": -1}
            )
            
            assert response.status_code == 422  # Validation error
    
    def test_calculate_power_missing_fields(self):
        """Test power calculation with missing fields."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/power/",
                json={"base": 2}
            )
            
            assert response.status_code == 422


class TestFibonacciAPI:
    """Integration tests for Fibonacci endpoints."""
    
    def test_calculate_fibonacci_success(self):
        """Test successful Fibonacci calculation via API."""
        with TestClient(app) as client:
            response = client.get("/api/v1/fibonacci/5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["n"] == 5
            assert data["result"] == 5
    
    def test_calculate_fibonacci_zero(self):
        """Test Fibonacci calculation for n=0."""
        with TestClient(app) as client:
            response = client.get("/api/v1/fibonacci/0")
            
            assert response.status_code == 200
            data = response.json()
            assert data["n"] == 0
            assert data["result"] == 0
    
    def test_calculate_fibonacci_large_number(self):
        """Test Fibonacci calculation for larger number."""
        with TestClient(app) as client:
            response = client.get("/api/v1/fibonacci/10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["n"] == 10
            assert data["result"] == 55


class TestFactorialAPI:
    """Integration tests for factorial endpoints."""
    
    def test_calculate_factorial_success(self):
        """Test successful factorial calculation via API."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/factorial/",
                json={"n": 5}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["n"] == 5
            assert data["result"] == 120
    
    def test_calculate_factorial_zero(self):
        """Test factorial calculation for n=0."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/factorial/",
                json={"n": 0}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["n"] == 0
            assert data["result"] == 1
    
    def test_calculate_factorial_validation_error(self):
        """Test factorial calculation with invalid input."""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/factorial/",
                json={"n": -1}
            )
            
            assert response.status_code == 422  # Validation error


class TestHealthEndpoints:
    """Tests for health and monitoring endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        with TestClient(app) as client:
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "math-service"
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        with TestClient(app) as client:
            response = client.get("/metrics")
            
            assert response.status_code == 200
            assert "text/plain" in response.headers["content-type"]

"""Unit tests for domain models."""

import pytest
from datetime import datetime

from domain.models import (
    FactorialRequest,
    FactorialResult,
    FibonacciResult,
    MathOperation,
    PowerRequest,
    PowerResult,
)


class TestPowerRequest:
    """Tests for PowerRequest value object."""
    
    def test_valid_power_request(self):
        """Test creating a valid power request."""
        request = PowerRequest(base=2, exponent=3)
        assert request.base == 2
        assert request.exponent == 3
    
    def test_negative_exponent_raises_error(self):
        """Test that negative exponent raises ValueError."""
        with pytest.raises(ValueError, match="Exponent must be non-negative"):
            PowerRequest(base=2, exponent=-1)
    
    def test_non_integer_base_raises_error(self):
        """Test that non-integer base raises ValueError."""
        with pytest.raises(ValueError, match="Base and exponent must be integers"):
            PowerRequest(base=2.5, exponent=3)


class TestFactorialRequest:
    """Tests for FactorialRequest value object."""
    
    def test_valid_factorial_request(self):
        """Test creating a valid factorial request."""
        request = FactorialRequest(n=5)
        assert request.n == 5
    
    def test_negative_n_raises_error(self):
        """Test that negative n raises ValueError."""
        with pytest.raises(ValueError, match="N must be non-negative"):
            FactorialRequest(n=-1)
    
    def test_non_integer_n_raises_error(self):
        """Test that non-integer n raises ValueError."""
        with pytest.raises(ValueError, match="N must be an integer"):
            FactorialRequest(n=5.5)


class TestResultModels:
    """Tests for result value objects."""
    
    def test_power_result_to_dict(self):
        """Test PowerResult to_dict method."""
        result = PowerResult(base=2, exponent=3, result=8)
        expected = {"base": 2, "exponent": 3, "result": 8}
        assert result.to_dict() == expected
    
    def test_fibonacci_result_to_dict(self):
        """Test FibonacciResult to_dict method."""
        result = FibonacciResult(n=5, result=5)
        expected = {"n": 5, "result": 5}
        assert result.to_dict() == expected
    
    def test_factorial_result_to_dict(self):
        """Test FactorialResult to_dict method."""
        result = FactorialResult(n=5, result=120)
        expected = {"n": 5, "result": 120}
        assert result.to_dict() == expected


class TestMathOperation:
    """Tests for MathOperation value object."""
    
    def test_math_operation_to_dict(self):
        """Test MathOperation to_dict method."""
        timestamp = datetime.utcnow()
        operation = MathOperation(
            operation_type="power",
            parameters={"base": 2, "exponent": 3},
            result=8,
            duration_ms=10.5,
            timestamp=timestamp,
        )
        
        result = operation.to_dict()
        
        assert result["operation_type"] == "power"
        assert result["parameters"] == {"base": 2, "exponent": 3}
        assert result["result"] == "8"
        assert result["duration_ms"] == 10.5
        assert result["timestamp"] == timestamp.isoformat()

"""Unit tests for services."""

import pytest
from unittest.mock import AsyncMock, Mock

from domain.models import FactorialRequest, PowerRequest
from services.factorial import FactorialService
from services.fibonacci import FibonacciService
from services.power import PowerService


class TestPowerService:
    """Tests for PowerService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def power_service(self, mock_repository):
        """Create PowerService with mock repository."""
        return PowerService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_calculate_power_success(self, power_service, mock_repository):
        """Test successful power calculation."""
        request = PowerRequest(base=2, exponent=3)
        
        result = await power_service.calculate_power(request)
        
        assert result.base == 2
        assert result.exponent == 3
        assert result.result == 8
        
        # Verify repository was called
        mock_repository.save_operation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_power_validation_error(self, power_service, mock_repository):
        """Test power calculation with validation error."""
        # This would fail validation in the service due to limits
        request = PowerRequest(base=10000, exponent=10000)
        
        with pytest.raises(ValueError):
            await power_service.calculate_power(request)


class TestFibonacciService:
    """Tests for FibonacciService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def fibonacci_service(self, mock_repository):
        """Create FibonacciService with mock repository."""
        return FibonacciService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_calculate_fibonacci_success(self, fibonacci_service, mock_repository):
        """Test successful Fibonacci calculation."""
        result = await fibonacci_service.calculate_fibonacci(5)
        
        assert result.n == 5
        assert result.result == 5  # 5th Fibonacci number is 5
        
        # Verify repository was called
        mock_repository.save_operation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_fibonacci_cached(self, fibonacci_service, mock_repository):
        """Test Fibonacci calculation uses cache."""
        # Calculate twice to test caching
        result1 = await fibonacci_service.calculate_fibonacci(10)
        result2 = await fibonacci_service.calculate_fibonacci(10)
        
        assert result1.result == result2.result
        assert result1.result == 55  # 10th Fibonacci number
    
    @pytest.mark.asyncio
    async def test_calculate_fibonacci_negative_error(self, fibonacci_service, mock_repository):
        """Test Fibonacci calculation with negative input."""
        with pytest.raises(ValueError, match="N must be non-negative"):
            await fibonacci_service.calculate_fibonacci(-1)


class TestFactorialService:
    """Tests for FactorialService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def factorial_service(self, mock_repository):
        """Create FactorialService with mock repository."""
        return FactorialService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_calculate_factorial_success(self, factorial_service, mock_repository):
        """Test successful factorial calculation."""
        request = FactorialRequest(n=5)
        
        result = await factorial_service.calculate_factorial(request)
        
        assert result.n == 5
        assert result.result == 120  # 5! = 120
        
        # Verify repository was called
        mock_repository.save_operation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_factorial_zero(self, factorial_service, mock_repository):
        """Test factorial of zero."""
        request = FactorialRequest(n=0)
        
        result = await factorial_service.calculate_factorial(request)
        
        assert result.n == 0
        assert result.result == 1  # 0! = 1
    
    @pytest.mark.asyncio
    async def test_calculate_factorial_one(self, factorial_service, mock_repository):
        """Test factorial of one."""
        request = FactorialRequest(n=1)
        
        result = await factorial_service.calculate_factorial(request)
        
        assert result.n == 1
        assert result.result == 1  # 1! = 1

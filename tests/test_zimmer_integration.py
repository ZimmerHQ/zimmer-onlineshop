"""
Tests for Zimmer integration.
Tests service token authentication, user management, and token consumption.
"""

import pytest
import os
import bcrypt
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from database import get_db, SessionLocal
from app.core.settings import SERVICE_TOKEN, SERVICE_TOKEN_HASH
from app.core.service_token import verify_service_token, require_service_token
from app.services.users_service import UsersService
from app.models.zimmer import AutomationUser, UserSession, UsageLedger

# Test client setup
@pytest.fixture
def client():
    """Create test client."""
    from main import app
    return TestClient(app)

@pytest.fixture
def db_session():
    """Create database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "user_id": "test_user_123",
        "automation_id": "18",
        "user_email": "test@example.com",
        "user_name": "Test User"
    }

class TestServiceToken:
    """Test service token authentication."""
    
    def test_verify_service_token_with_plain_token(self):
        """Test token verification with plain token (dev mode)."""
        # Set up test environment
        os.environ["SERVICE_TOKEN"] = "test_token_123"
        os.environ.pop("SERVICE_TOKEN_HASH", None)
        
        # Test valid token
        assert verify_service_token("test_token_123") == True
        
        # Test invalid token
        assert verify_service_token("wrong_token") == False
        assert verify_service_token("") == False
        assert verify_service_token(None) == False
    
    def test_verify_service_token_with_bcrypt_hash(self):
        """Test token verification with bcrypt hash."""
        # Set up test environment
        test_token = "test_token_123"
        token_hash = bcrypt.hashpw(test_token.encode('utf-8'), bcrypt.gensalt())
        
        os.environ["SERVICE_TOKEN_HASH"] = token_hash.decode('utf-8')
        os.environ.pop("SERVICE_TOKEN", None)
        
        # Test valid token
        assert verify_service_token(test_token) == True
        
        # Test invalid token
        assert verify_service_token("wrong_token") == False

class TestUsersService:
    """Test users service functionality."""
    
    def test_ensure_user_creation(self, db_session, test_user_data):
        """Test user creation."""
        users_service = UsersService(db_session)
        
        # Create user
        user = users_service.ensure_user(**test_user_data)
        
        assert user is not None
        assert user.user_id == test_user_data["user_id"]
        assert user.automation_id == test_user_data["automation_id"]
        assert user.user_email == test_user_data["user_email"]
        assert user.user_name == test_user_data["user_name"]
        assert user.tokens_remaining == 0  # Default value
        assert user.demo_tokens == 0  # Default value
    
    def test_ensure_user_upsert(self, db_session, test_user_data):
        """Test user upsert (update existing)."""
        users_service = UsersService(db_session)
        
        # Create user first time
        user1 = users_service.ensure_user(**test_user_data)
        
        # Update user
        updated_data = test_user_data.copy()
        updated_data["user_name"] = "Updated User"
        updated_data["tokens_remaining"] = 100
        
        user2 = users_service.ensure_user(**updated_data)
        
        assert user1.id == user2.id  # Same user
        assert user2.user_name == "Updated User"
        assert user2.tokens_remaining == 100
    
    def test_update_tokens(self, db_session, test_user_data):
        """Test token updates."""
        users_service = UsersService(db_session)
        
        # Create user
        user = users_service.ensure_user(**test_user_data)
        initial_tokens = user.tokens_remaining
        
        # Add tokens
        new_balance = users_service.update_tokens(
            user_id=test_user_data["user_id"],
            automation_id=test_user_data["automation_id"],
            delta=50,
            reason="top_up",
            meta={"source": "test"}
        )
        
        assert new_balance == initial_tokens + 50
        
        # Consume tokens
        new_balance = users_service.update_tokens(
            user_id=test_user_data["user_id"],
            automation_id=test_user_data["automation_id"],
            delta=-20,
            reason="chat",
            meta={"source": "test"}
        )
        
        assert new_balance == initial_tokens + 30  # 50 - 20
    
    def test_update_tokens_negative_balance(self, db_session, test_user_data):
        """Test that tokens cannot go below zero."""
        users_service = UsersService(db_session)
        
        # Create user
        users_service.ensure_user(**test_user_data)
        
        # Try to consume more tokens than available
        new_balance = users_service.update_tokens(
            user_id=test_user_data["user_id"],
            automation_id=test_user_data["automation_id"],
            delta=-100,
            reason="chat",
            meta={"source": "test"}
        )
        
        assert new_balance == 0  # Should not go below zero

class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_dashboard_endpoint(self, client, test_user_data):
        """Test dashboard endpoint."""
        response = client.get(
            "/dashboard",
            params=test_user_data
        )
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "خوش آمدید" in response.text  # Persian welcome message
        assert "توکن‌های باقیمانده" in response.text  # Persian token label
    
    def test_provision_endpoint_without_token(self, client):
        """Test provision endpoint without service token."""
        response = client.post(
            "/api/provision",
            json={
                "user_automation_id": "123",
                "user_id": "test_user",
                "bot_token": "bot_token_123",
                "demo_tokens": 100
            }
        )
        
        assert response.status_code == 401
        assert "Missing X-Zimmer-Service-Token header" in response.json()["detail"]
    
    def test_provision_endpoint_with_invalid_token(self, client):
        """Test provision endpoint with invalid service token."""
        response = client.post(
            "/api/provision",
            json={
                "user_automation_id": "123",
                "user_id": "test_user",
                "bot_token": "bot_token_123",
                "demo_tokens": 100
            },
            headers={"X-Zimmer-Service-Token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid service token" in response.json()["detail"]
    
    @patch.dict(os.environ, {"SERVICE_TOKEN": "test_token_123"})
    def test_provision_endpoint_with_valid_token(self, client):
        """Test provision endpoint with valid service token."""
        response = client.post(
            "/api/provision",
            json={
                "user_automation_id": "123",
                "user_id": "test_user",
                "bot_token": "bot_token_123",
                "demo_tokens": 100
            },
            headers={"X-Zimmer-Service-Token": "test_token_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "webhook_url" in data
        assert "test_user" in data["webhook_url"]
    
    def test_consume_tokens_internal(self, client, test_user_data):
        """Test internal token consumption."""
        # First create a user via dashboard
        client.get("/dashboard", params=test_user_data)
        
        # Then consume tokens
        response = client.post(
            "/api/consume-tokens",
            json={
                "user_id": test_user_data["user_id"],
                "automation_id": test_user_data["automation_id"],
                "tokens_consumed": 10,
                "action": "chat"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "remaining_tokens" in data
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "uptime" in data
        assert "database_status" in data

class TestUsageForwarder:
    """Test usage forwarder functionality."""
    
    @patch('app.services.usage_forwarder.httpx.AsyncClient')
    async def test_forward_usage_success(self, mock_client):
        """Test successful usage forwarding."""
        from app.services.usage_forwarder import UsageForwarder
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        forwarder = UsageForwarder()
        forwarder.platform_url = "https://api.zimmerai.com"
        forwarder.service_token = "test_token"
        
        usage_data = {
            "user_automation_id": "123",
            "tokens_consumed": 10,
            "action": "chat"
        }
        
        # Should not raise exception
        await forwarder.forward_usage_to_platform(usage_data)
    
    @patch('app.services.usage_forwarder.httpx.AsyncClient')
    async def test_forward_usage_network_error(self, mock_client):
        """Test usage forwarding with network error."""
        from app.services.usage_forwarder import UsageForwarder
        
        # Mock network error
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
        
        forwarder = UsageForwarder()
        forwarder.platform_url = "https://api.zimmerai.com"
        forwarder.service_token = "test_token"
        
        usage_data = {
            "user_automation_id": "123",
            "tokens_consumed": 10,
            "action": "chat"
        }
        
        # Should not raise exception (swallows errors)
        await forwarder.forward_usage_to_platform(usage_data)
    
    def test_forwarder_not_configured(self):
        """Test forwarder when not configured."""
        from app.services.usage_forwarder import UsageForwarder
        
        forwarder = UsageForwarder()
        forwarder.platform_url = None
        forwarder.service_token = None
        
        assert forwarder.is_configured() == False


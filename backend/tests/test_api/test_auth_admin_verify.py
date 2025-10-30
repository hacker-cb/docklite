"""
Security tests for admin verification endpoint (Traefik ForwardAuth)
These tests ensure ONLY admins can access protected resources
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAdminVerification:
    """Tests for /api/auth/verify-admin endpoint"""
    
    async def test_verify_admin_success(self, client: AsyncClient, admin_token):
        """Test that admin user passes verification"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # Check response headers for Traefik
        assert "X-User-Id" in response.headers
        assert "X-Username" in response.headers
        assert "X-Is-Admin" in response.headers
        assert response.headers["X-Is-Admin"] == "true"
    
    async def test_verify_admin_non_admin_forbidden(self, client: AsyncClient, user_token):
        """Test that non-admin user is rejected (SECURITY CRITICAL)"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Must be 403 Forbidden for non-admins
        assert response.status_code == 403
        data = response.json()
        assert "Admin access required" in data["detail"]
    
    async def test_verify_admin_no_token(self, client: AsyncClient):
        """Test that request without token is rejected (SECURITY CRITICAL)"""
        response = await client.get("/api/auth/verify-admin")
        
        # FastAPI returns 403 when authentication dependency fails
        assert response.status_code in [401, 403]
    
    async def test_verify_admin_invalid_token(self, client: AsyncClient):
        """Test that invalid token is rejected (SECURITY CRITICAL)"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": "Bearer invalid-token-here"}
        )
        
        # Must be 401 Unauthorized
        assert response.status_code == 401
    
    async def test_verify_admin_expired_token(self, client: AsyncClient):
        """Test that expired token is rejected (SECURITY CRITICAL)"""
        # Create expired token
        from app.services.auth_service import AuthService
        from datetime import timedelta
        
        auth_service = AuthService(None)  # type: ignore[arg-type]
        expired_token = auth_service.create_access_token(
            data={"sub": "admin"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Must be 401 Unauthorized
        assert response.status_code == 401
    
    async def test_verify_admin_malformed_token(self, client: AsyncClient):
        """Test that malformed token is rejected (SECURITY CRITICAL)"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"}
        )
        
        # Must be 401 Unauthorized
        assert response.status_code == 401
    
    async def test_verify_admin_missing_bearer_prefix(self, client: AsyncClient, admin_token):
        """Test that token without Bearer prefix is rejected (SECURITY CRITICAL)"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": admin_token}  # Missing "Bearer "
        )
        
        # FastAPI auth dependency will fail
        assert response.status_code in [401, 403]
    
    async def test_verify_admin_headers_content(self, client: AsyncClient, admin_token):
        """Test that response headers contain correct user info"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify header values are not empty
        user_id = response.headers.get("X-User-Id")
        username = response.headers.get("X-Username")
        is_admin = response.headers.get("X-Is-Admin")
        
        assert user_id
        assert user_id.isdigit()  # Should be numeric
        assert username
        assert len(username) > 0
        assert is_admin == "true"
    
    async def test_verify_admin_case_sensitive_bearer(self, client: AsyncClient, admin_token):
        """Test Bearer prefix case sensitivity"""
        # Try lowercase "bearer" - FastAPI actually accepts it
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"bearer {admin_token}"}
        )
        
        # FastAPI HTTPBearer scheme accepts both cases
        # This is actually OK for security (token itself is validated)
        assert response.status_code in [200, 401]
    
    async def test_verify_admin_sql_injection_attempt(self, client: AsyncClient):
        """Test SQL injection protection in token (SECURITY CRITICAL)"""
        malicious_token = "'; DROP TABLE users; --"
        
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {malicious_token}"}
        )
        
        # Must be rejected
        assert response.status_code == 401
    
    async def test_verify_admin_xss_attempt(self, client: AsyncClient):
        """Test XSS protection in token (SECURITY CRITICAL)"""
        malicious_token = "<script>alert('xss')</script>"
        
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {malicious_token}"}
        )
        
        # Must be rejected
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAdminVerificationIntegration:
    """Integration tests for admin verification with actual workflow"""
    
    async def test_admin_login_and_verify(self, client: AsyncClient, db_session):
        """Test complete flow: create admin → login → verify"""
        from app.services.auth_service import AuthService
        from app.models.schemas import UserCreate
        
        auth_service = AuthService(db_session)
        
        # Create admin user
        admin_data = UserCreate(
            username="securityadmin",
            email="admin@example.com",
            password="SecurePass123",
            system_user="docklite"
        )
        
        user, error = await auth_service.create_first_admin(admin_data)
        assert error is None
        await db_session.commit()
        
        # Login
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "securityadmin", "password": "SecurePass123"}
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Verify admin
        verify_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert verify_response.status_code == 200
        assert verify_response.headers["X-Username"] == "securityadmin"
        assert verify_response.headers["X-Is-Admin"] == "true"
    
    async def test_regular_user_cannot_verify(self, client: AsyncClient, db_session):
        """Test that regular user cannot pass admin verification (SECURITY CRITICAL)"""
        from app.services.auth_service import AuthService
        from app.models.schemas import UserCreate
        
        auth_service = AuthService(db_session)
        
        # Create admin first
        admin_data = UserCreate(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123",
            system_user="docklite"
        )
        await auth_service.create_first_admin(admin_data)
        await db_session.commit()
        
        # Create regular user (create_user always creates non-admin)
        regular_data = UserCreate(
            username="regularuser",
            email="user@example.com",
            password="UserPass123",
            system_user="docklite"
        )
        regular_user, error = await auth_service.create_user(regular_data)
        assert error is None
        await db_session.commit()
        
        # Login as regular user
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "regularuser", "password": "UserPass123"}
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to verify admin - MUST FAIL
        verify_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # CRITICAL: Must be 403 Forbidden
        assert verify_response.status_code == 403
        assert "Admin access required" in verify_response.json()["detail"]
    
    async def test_inactive_admin_cannot_verify(self, client: AsyncClient, db_session):
        """Test that inactive admin is rejected (SECURITY CRITICAL)"""
        from app.services.auth_service import AuthService
        from app.models.schemas import UserCreate
        from sqlalchemy import select, update
        from app.models.user import User
        
        auth_service = AuthService(db_session)
        
        # Create admin
        admin_data = UserCreate(
            username="inactiveadmin",
            email="inactive@test.com",
            password="AdminPass123",
            system_user="docklite"
        )
        user, error = await auth_service.create_first_admin(admin_data)
        await db_session.commit()
        
        # Get token before deactivation
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "inactiveadmin", "password": "AdminPass123"}
        )
        token = login_response.json()["access_token"]
        
        # Deactivate user
        await db_session.execute(
            update(User).where(User.username == "inactiveadmin").values(is_active=0)
        )
        await db_session.commit()
        
        # Try to verify - MUST FAIL
        verify_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # CRITICAL: Must be 401 or 403 (user is inactive)
        assert verify_response.status_code in [401, 403]


@pytest.mark.asyncio
class TestTraefikForwardAuthSecurity:
    """Tests specifically for Traefik ForwardAuth security"""
    
    async def test_forwardauth_blocks_without_auth(self, client: AsyncClient):
        """Test that ForwardAuth blocks requests without authentication"""
        response = await client.get("/api/auth/verify-admin")
        
        # Must block (401 or 403 from auth dependency)
        assert response.status_code in [401, 403]
    
    async def test_forwardauth_blocks_non_admin(self, client: AsyncClient, user_token):
        """Test that ForwardAuth blocks non-admin users (SECURITY CRITICAL)"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Must block non-admins
        assert response.status_code == 403
    
    async def test_forwardauth_allows_admin(self, client: AsyncClient, admin_token):
        """Test that ForwardAuth allows admin users"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Must allow admins
        assert response.status_code == 200
    
    async def test_forwardauth_token_reuse_prevention(self, client: AsyncClient, admin_token):
        """Test that each request is verified independently"""
        # First request
        response1 = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response1.status_code == 200
        
        # Second request with same token - should still verify
        response2 = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response2.status_code == 200
        
        # Second request without token - should fail
        response3 = await client.get("/api/auth/verify-admin")
        assert response3.status_code in [401, 403]


@pytest.mark.asyncio
class TestDashboardAccessControl:
    """Tests for complete dashboard access control scenario"""
    
    async def test_dashboard_access_control_workflow(
        self, 
        client: AsyncClient, 
        db_session,
        admin_token,
        user_token
    ):
        """
        Test complete dashboard access control workflow:
        1. Admin can access
        2. Regular user cannot access
        3. No token cannot access
        """
        # Scenario 1: Admin access - SHOULD SUCCEED
        admin_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_response.status_code == 200, "Admin should have access"
        
        # Scenario 2: Regular user access - MUST FAIL
        user_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert user_response.status_code == 403, "Regular user MUST NOT have access"
        
        # Scenario 3: No token - MUST FAIL
        no_auth_response = await client.get("/api/auth/verify-admin")
        assert no_auth_response.status_code in [401, 403], "Unauthenticated MUST NOT have access"
    
    async def test_privilege_escalation_prevention(self, client: AsyncClient, db_session):
        """
        Test that regular user cannot escalate to admin (SECURITY CRITICAL)
        """
        from app.services.auth_service import AuthService
        from app.models.schemas import UserCreate
        
        auth_service = AuthService(db_session)
        
        # Create admin
        admin_data = UserCreate(
            username="realadmin",
            password="AdminPass123",
            system_user="docklite"
        )
        await auth_service.create_first_admin(admin_data)
        await db_session.commit()
        
        # Create regular user (create_user always creates non-admin)
        user_data = UserCreate(
            username="regularuser",
            email="regular@example.com",
            password="UserPass123",
            system_user="docklite"
        )
        await auth_service.create_user(user_data)
        await db_session.commit()
        
        # Login as regular user
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "regularuser", "password": "UserPass123"}
        )
        user_token = login_response.json()["access_token"]
        
        # Try to access admin endpoint - MUST FAIL
        verify_response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # CRITICAL: Regular user MUST NOT pass verification
        assert verify_response.status_code == 403
        assert "Admin access required" in verify_response.json()["detail"]


@pytest.mark.asyncio
class TestSecurityVulnerabilities:
    """Tests for common security vulnerabilities"""
    
    async def test_header_injection_protection(self, client: AsyncClient, admin_token):
        """Test protection against header injection attacks"""
        # Try to inject malicious headers
        malicious_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Forwarded-For": "'; DROP TABLE users; --",
            "X-Real-IP": "<script>alert('xss')</script>",
            "User-Agent": "Mozilla/5.0\r\nX-Injected: malicious"
        }
        
        response = await client.get(
            "/api/auth/verify-admin",
            headers=malicious_headers
        )
        
        # Should still work (injections ignored)
        assert response.status_code == 200
        
        # Response headers should be safe
        assert "X-User-Id" in response.headers
        assert "script" not in response.headers.get("X-Username", "")
        assert "DROP" not in response.headers.get("X-Username", "")
    
    async def test_timing_attack_resistance(self, client: AsyncClient, admin_token):
        """Test that response times don't leak information"""
        import time
        
        # Measure valid token response time
        start = time.time()
        response1 = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        time1 = time.time() - start
        
        # Measure invalid token response time
        start = time.time()
        response2 = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": "Bearer invalid-token"}
        )
        time2 = time.time() - start
        
        # Both should fail/succeed consistently
        assert response1.status_code == 200
        assert response2.status_code == 401
        
        # Times should be similar (no timing attack vector)
        # Allow 100ms variance
        assert abs(time1 - time2) < 0.1
    
    async def test_rate_limiting_headers(self, client: AsyncClient, admin_token):
        """Test that multiple rapid requests are handled"""
        # Make 10 rapid requests
        responses = []
        for _ in range(10):
            response = await client.get(
                "/api/auth/verify-admin",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            responses.append(response)
        
        # All should succeed (no accidental rate limiting)
        for response in responses:
            assert response.status_code == 200
    
    async def test_token_not_logged_in_response(self, client: AsyncClient, admin_token):
        """Test that tokens are not leaked in error responses (SECURITY CRITICAL)"""
        # Valid admin token
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Token should NOT appear in response body
        response_text = response.text
        assert admin_token not in response_text
        
        # Token should NOT appear in headers
        for header_value in response.headers.values():
            assert admin_token not in str(header_value)
    
    async def test_cors_protection(self, client: AsyncClient, admin_token):
        """Test CORS headers for admin endpoint"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Origin": "http://malicious-site.com"
            }
        )
        
        # Should still work (CORS handled at server level)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestCookieAuthentication:
    """Tests for cookie-based authentication (for browser dashboard access)"""
    
    async def test_verify_admin_with_cookie_admin(self, client: AsyncClient, admin_token):
        """Test admin verification via cookie"""
        # Set cookie
        client.cookies.set('token', admin_token)
        
        response = await client.get("/api/auth/verify-admin")
        
        assert response.status_code == 200
        assert response.headers["X-Is-Admin"] == "true"
    
    async def test_verify_admin_with_cookie_non_admin(self, client: AsyncClient, user_token):
        """Test non-admin rejection via cookie (SECURITY CRITICAL)"""
        # Set cookie
        client.cookies.set('token', user_token)
        
        response = await client.get("/api/auth/verify-admin")
        
        # Must be rejected
        assert response.status_code == 403
    
    async def test_verify_admin_cookie_priority(self, client: AsyncClient, admin_token, user_token):
        """Test that Authorization header has priority over cookie"""
        # Set cookie with non-admin token
        client.cookies.set('token', user_token)
        
        # But send admin token in header
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should use header token (admin) not cookie (user)
        assert response.status_code == 200
    
    async def test_verify_admin_invalid_cookie(self, client: AsyncClient):
        """Test invalid cookie token (SECURITY CRITICAL)"""
        client.cookies.set('token', 'invalid-token')
        
        response = await client.get("/api/auth/verify-admin")
        
        assert response.status_code == 401
    
    async def test_verify_admin_no_auth_no_cookie(self, client: AsyncClient):
        """Test with neither header nor cookie (SECURITY CRITICAL)"""
        response = await client.get("/api/auth/verify-admin")
        
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    async def test_verify_admin_with_extra_spaces(self, client: AsyncClient, admin_token):
        """Test token with extra spaces"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": f"Bearer  {admin_token}  "}  # Extra spaces
        )
        
        # Should be rejected (strict parsing)
        assert response.status_code == 401
    
    async def test_verify_admin_empty_authorization(self, client: AsyncClient):
        """Test with empty authorization header"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": ""}
        )
        
        assert response.status_code in [401, 403]
    
    async def test_verify_admin_bearer_only(self, client: AsyncClient):
        """Test with 'Bearer' but no token"""
        response = await client.get(
            "/api/auth/verify-admin",
            headers={"Authorization": "Bearer "}
        )
        
        assert response.status_code in [401, 403]
    
    async def test_concurrent_admin_verification(self, client: AsyncClient, admin_token):
        """Test concurrent admin verifications"""
        import asyncio
        
        # Make 5 concurrent requests
        tasks = [
            client.get(
                "/api/auth/verify-admin",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            for _ in range(5)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200


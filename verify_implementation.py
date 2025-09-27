#!/usr/bin/env python3
"""
Zimmer Implementation Verification Script
Validates the implementation without requiring a running server
"""

import os
import sys
import importlib.util

def verify_imports():
    """Verify all required modules can be imported."""
    print("🔍 Verifying imports...")
    
    try:
        # Test config import
        from config_root import (
            ZIMMER_SERVICE_TOKEN, CHAT_BUDGET_SECONDS, CHAT_API_TIMEOUT,
            LLM_TIMEOUT, AGENT_MAX_ITERS, CHAT_MODEL, load_config_override
        )
        print("✅ Config imports: PASS")
        
        # Test models import
        from models import ZimmerTenant
        print("✅ Models import: PASS")
        
        # Test schemas import
        from schemas.zimmer import (
            ZimmerProvisionRequest, ZimmerProvisionResponse,
            ZimmerUsageRequest, ZimmerUsageResponse,
            ZimmerKBStatusResponse, ZimmerKBResetResponse
        )
        print("✅ Schemas import: PASS")
        
        # Test services import
        from services.zimmer_service import (
            provision_tenant, consume_usage, get_kb_status, reset_kb
        )
        print("✅ Services import: PASS")
        
        # Test routers import
        from routers.zimmer import router as zimmer_router
        from routers.health import router as health_router
        print("✅ Routers import: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Import verification: FAIL - {str(e)}")
        return False

def verify_config():
    """Verify configuration is properly set up."""
    print("\n🔍 Verifying configuration...")
    
    try:
        from config_root import load_config_override
        
        config = load_config_override()
        required_keys = [
            "ZIMMER_SERVICE_TOKEN", "CHAT_BUDGET_SECONDS", "CHAT_API_TIMEOUT",
            "LLM_TIMEOUT", "AGENT_MAX_ITERS", "CHAT_MODEL"
        ]
        
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing config key: {key}")
                return False
        
        print("✅ Configuration: PASS")
        print(f"   CHAT_BUDGET_SECONDS: {config['CHAT_BUDGET_SECONDS']}")
        print(f"   CHAT_API_TIMEOUT: {config['CHAT_API_TIMEOUT']}")
        print(f"   LLM_TIMEOUT: {config['LLM_TIMEOUT']}")
        print(f"   AGENT_MAX_ITERS: {config['AGENT_MAX_ITERS']}")
        print(f"   CHAT_MODEL: {config['CHAT_MODEL']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration verification: FAIL - {str(e)}")
        return False

def verify_models():
    """Verify database models are properly defined."""
    print("\n🔍 Verifying database models...")
    
    try:
        from models import ZimmerTenant
        
        # Check required fields exist
        required_fields = [
            'user_automation_id', 'user_id', 'integration_status', 'service_url',
            'demo_tokens', 'paid_tokens', 'kb_status', 'kb_last_updated',
            'kb_total_documents', 'kb_healthy'
        ]
        
        # Get model columns
        columns = [column.name for column in ZimmerTenant.__table__.columns]
        
        for field in required_fields:
            if field not in columns:
                print(f"❌ Missing model field: {field}")
                return False
        
        print("✅ Database models: PASS")
        print(f"   ZimmerTenant has {len(columns)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Model verification: FAIL - {str(e)}")
        return False

def verify_schemas():
    """Verify Pydantic schemas are properly defined."""
    print("\n🔍 Verifying Pydantic schemas...")
    
    try:
        from schemas.zimmer import (
            ZimmerProvisionRequest, ZimmerProvisionResponse,
            ZimmerUsageRequest, ZimmerUsageResponse,
            ZimmerKBStatusResponse, ZimmerKBResetResponse
        )
        
        # Test schema instantiation
        provision_req = ZimmerProvisionRequest(
            user_automation_id=123,
            user_id=456,
            demo_tokens=1000,
            service_url="https://example.com"
        )
        
        usage_req = ZimmerUsageRequest(
            user_automation_id=123,
            units=10,
            usage_type="chat",
            meta={"test": "data"}
        )
        
        print("✅ Pydantic schemas: PASS")
        print(f"   Provision request: {provision_req.user_automation_id}")
        print(f"   Usage request: {usage_req.units} units")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema verification: FAIL - {str(e)}")
        return False

def verify_endpoints():
    """Verify endpoint definitions exist."""
    print("\n🔍 Verifying endpoint definitions...")
    
    try:
        from routers.zimmer import router as zimmer_router
        from routers.health import router as health_router
        
        # Check Zimmer router has required routes
        zimmer_routes = [route.path for route in zimmer_router.routes]
        required_zimmer_routes = [
            "/api/zimmer/provision",
            "/api/zimmer/usage/consume", 
            "/api/zimmer/kb/status",
            "/api/zimmer/kb/reset"
        ]
        
        for route in required_zimmer_routes:
            if not any(route in r for r in zimmer_routes):
                print(f"❌ Missing Zimmer route: {route}")
                return False
        
        # Check health router has health route
        health_routes = [route.path for route in health_router.routes]
        if not any("/health" in r or r == "/" for r in health_routes):
            print("❌ Missing health route")
            return False
        
        print("✅ Endpoint definitions: PASS")
        print(f"   Zimmer routes: {len(zimmer_routes)}")
        print(f"   Health routes: {len(health_routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint verification: FAIL - {str(e)}")
        return False

def verify_documentation():
    """Verify documentation files exist."""
    print("\n🔍 Verifying documentation...")
    
    try:
        # Check README exists
        if not os.path.exists("ZIMMER_INTEGRATION_README.md"):
            print("❌ Missing ZIMMER_INTEGRATION_README.md")
            return False
        
        # Check test script exists
        if not os.path.exists("test_zimmer_integration.py"):
            print("❌ Missing test_zimmer_integration.py")
            return False
        
        # Read README content
        with open("ZIMMER_INTEGRATION_README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for required curl examples
        required_curls = [
            "curl -X GET \"$BASE/health\"",
            "curl -X POST \"$BASE/api/zimmer/provision\"",
            "curl -X POST \"$BASE/api/zimmer/usage/consume\"",
            "curl -X GET \"$BASE/api/zimmer/kb/status",
            "curl -X POST \"$BASE/api/zimmer/kb/reset",
            "curl -X POST \"$BASE/api/chat\""
        ]
        
        for curl in required_curls:
            if curl not in content:
                print(f"❌ Missing curl example: {curl}")
                return False
        
        print("✅ Documentation: PASS")
        print("   README with curl examples: ✓")
        print("   Test script: ✓")
        
        return True
        
    except Exception as e:
        print(f"❌ Documentation verification: FAIL - {str(e)}")
        return False

def main():
    """Run all verification checks."""
    print("🚀 Zimmer Implementation Verification")
    print("=" * 50)
    
    checks = [
        verify_imports,
        verify_config,
        verify_models,
        verify_schemas,
        verify_endpoints,
        verify_documentation
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All verification checks passed!")
        print("\n✅ Implementation Summary:")
        print("   • All required modules import successfully")
        print("   • Configuration is properly set up with override hook")
        print("   • Database models include all required fields")
        print("   • Pydantic schemas validate correctly")
        print("   • All Zimmer endpoints are defined")
        print("   • Documentation includes required curl examples")
        print("\n🚀 Ready for Zimmer platform validation!")
        return True
    else:
        print("❌ Some verification checks failed.")
        print("Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

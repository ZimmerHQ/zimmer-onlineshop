# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Smoke test script for the FastAPI backend.
Tests all core endpoints and provides a PASS/FAIL summary.
"""

import os
import sys
import io
import time
import requests
import json
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Fix stdout encoding for Windows compatibility
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Emoji fallback for terminals that don't support UTF-8
SUPPORTS_EMOJI = sys.stdout.encoding and "utf" in sys.stdout.encoding.lower()
OK = "✅" if SUPPORTS_EMOJI else "OK"
FAIL = "❌" if SUPPORTS_EMOJI else "FAIL"
ROCKET = "🚀" if SUPPORTS_EMOJI else "[SMOKE]"
SUMMARY = "📊" if SUPPORTS_EMOJI else "[SUMMARY]"
ARROW = "➡️" if SUPPORTS_EMOJI else "->"
BOMB = "💥" if SUPPORTS_EMOJI else "[ERROR]"
SEARCH = "🔍" if SUPPORTS_EMOJI else "[DETAILS]"
CHART = "📈" if SUPPORTS_EMOJI else "[CHART]"
LIGHTNING = "⚡" if SUPPORTS_EMOJI else "[START]"

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir.parent / ".env")
except ImportError:
    pass

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10

# Test endpoints to check
ENDPOINTS = [
    ("GET", "/api/health/", "Basic health check"),
    ("GET", "/api/health/details", "Detailed health check"),
    ("GET", "/api/categories/exists", "Categories existence check"),
    ("GET", "/api/categories/summary", "Categories summary"),
    ("GET", "/api/products?q=test", "Product search"),
]

class SmokeTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Tuple[str, str, str, bool, str]] = []
        self.backend_process: Optional[subprocess.Popen] = None
        self.auto_started_backend = False
        
    def test_endpoint(self, method: str, endpoint: str, description: str) -> None:
        """Test a single endpoint and record results."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            else:
                response = requests.post(url, timeout=TIMEOUT)
            
            success = 200 <= response.status_code < 300
            
            # Try to parse response
            try:
                response_data = response.json()
                response_summary = str(response_data)[:100] + "..." if len(str(response_data)) > 100 else str(response_data)
            except:
                response_summary = f"Status: {response.status_code}, Text: {response.text[:100]}..."
            
            self.results.append((method, endpoint, description, success, response_summary))
            
        except requests.exceptions.RequestException as e:
            self.results.append((method, endpoint, description, False, f"Request failed: {str(e)}"))
        except Exception as e:
            self.results.append((method, endpoint, description, False, f"Unexpected error: {str(e)}"))
    
    def check_backend_health(self) -> bool:
        """Check if backend is reachable."""
        try:
            response = requests.get(f"{self.base_url}/api/health/", timeout=5)
            return response.status_code == 200 and response.json().get("status") == "ok"
        except:
            return False
    
    def wait_for_backend(self, timeout: int = 60) -> bool:
        """Wait for backend to become healthy."""
        print(f"Waiting for backend to be ready (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_backend_health():
                return True
            elapsed = int(time.time() - start_time)
            print(f"  Still waiting... ({elapsed}s elapsed)")
            
            # Check for backend output/errors
            if self.backend_process:
                try:
                    # Non-blocking check for output
                    if self.backend_process.poll() is not None:
                        # Process has terminated
                        stdout, stderr = self.backend_process.communicate()
                        if stderr:
                            print(f"  Backend error: {stderr.decode('utf-8', errors='ignore')[:200]}")
                        if stdout:
                            print(f"  Backend output: {stdout.decode('utf-8', errors='ignore')[:200]}")
                        return False
                except:
                    pass
            
            time.sleep(3)
        
        return False
    
    def start_backend(self) -> bool:
        """Start backend in a subprocess."""
        try:
            print(f"{LIGHTNING} Backend not running, starting uvicorn...")
            
            # Determine the correct command based on platform
            if sys.platform == "win32":
                # Windows
                cmd = ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
            else:
                # Linux/macOS
                cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
            
            print(f"Starting command: {' '.join(cmd)}")
            
            # Start backend process
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent.parent,  # backend directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            self.auto_started_backend = True
            print(f"Backend process started (PID: {self.backend_process.pid})")
            
            # Give the backend a moment to start up
            print("Giving backend 5 seconds to initialize...")
            time.sleep(5)
            
            # Wait for backend to be ready
            if self.wait_for_backend():
                print(f"{OK} Backend is up")
                return True
            else:
                print(f"{FAIL} Backend failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"{FAIL} Failed to start backend: {e}")
            return False
    
    def ensure_backend_running(self) -> bool:
        """Ensure backend is running, start if necessary."""
        # Try to connect to existing backend first
        for attempt in range(3):
            if self.check_backend_health():
                print(f"{OK} Backend is already running")
                return True
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(1)
        
        # Backend not running, start it
        return self.start_backend()
    
    def cleanup_backend(self) -> None:
        """Clean up backend process if we started it."""
        if self.backend_process and self.auto_started_backend:
            try:
                print(f"Cleaning up auto-started backend (PID: {self.backend_process.pid})...")
                
                if sys.platform == "win32":
                    # Windows: use taskkill for more reliable termination
                    subprocess.run(["taskkill", "/F", "/PID", str(self.backend_process.pid)], 
                                 capture_output=True, timeout=5)
                else:
                    # Linux/macOS: send SIGTERM, then SIGKILL if needed
                    self.backend_process.terminate()
                    try:
                        self.backend_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.backend_process.kill()
                        self.backend_process.wait()
                
                print(f"{OK} Backend process terminated")
                
            except Exception as e:
                print(f"{FAIL} Failed to terminate backend process: {e}")
    
    def run_all_tests(self) -> None:
        """Run all endpoint tests."""
        print("{} Starting smoke tests against: {}".format(ROCKET, self.base_url))
        print("=" * 80)
        
        for method, endpoint, description in ENDPOINTS:
            print("Testing: {} {}".format(method, endpoint))
            self.test_endpoint(method, endpoint, description)
        
        print("\n" + "=" * 80)
        self.print_results()
    
    def print_results(self) -> None:
        """Print test results in a formatted table."""
        print("{} SMOKE TEST RESULTS".format(SUMMARY))
        print("=" * 80)
        print("{:<6} {:<35} {:<6} {:<25}".format("Method", "Endpoint", "Status", "Description"))
        print("-" * 80)
        
        all_passed = True
        for method, endpoint, description, success, response in self.results:
            status = "PASS" if success else "FAIL"
            if not success:
                all_passed = False
            
            # Truncate long endpoints for display
            display_endpoint = endpoint if len(endpoint) <= 34 else endpoint[:31] + "..."
            display_description = description if len(description) <= 24 else description[:21] + "..."
            
            print("{:<6} {:<35} {:<6} {:<25}".format(method, display_endpoint, status, display_description))
        
        print("-" * 80)
        
        # Summary
        passed_count = sum(1 for _, _, _, success, _ in self.results if success)
        total_count = len(self.results)
        
        print("\n{} SUMMARY: {}/{} tests passed".format(CHART, passed_count, total_count))
        
        if all_passed:
            print("{} ALL TESTS PASSED - System is healthy!".format(OK))
        else:
            print("{} SOME TESTS FAILED - Check the details above".format(FAIL))
            print("\n{} DETAILED RESPONSES:".format(SEARCH))
            for method, endpoint, description, success, response in self.results:
                if not success:
                    print("\n{} {}:".format(method, endpoint))
                    print("  Response: {}".format(response))
        
        # Exit code
        sys.exit(0 if all_passed else 1)
    
    def get_results(self) -> tuple:
        """Get test results summary."""
        passed = sum(1 for _, _, _, success, _ in self.results)
        total = len(self.results)
        return passed, total


def main():
    """Main function to run smoke tests."""
    smoke_test = None
    try:
        smoke_test = SmokeTest(BASE_URL)
        
        # Ensure backend is running before starting tests
        if not smoke_test.ensure_backend_running():
            print(f"{FAIL} Backend failed to start. Exiting.")
            sys.exit(1)
        
        # Run the smoke tests
        smoke_test.run_all_tests()
        
        # Get results and print summary
        passed, total = smoke_test.get_results()
        print(f"\n{CHART} SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print(f"{OK} ALL TESTS PASSED - System is healthy!")
        else:
            print(f"{FAIL} SOME TESTS FAILED - Check the details above")
            print(f"\n{SEARCH} DETAILED RESPONSES:")
            for method, endpoint, description, success, response in smoke_test.results:
                if not success:
                    print(f"\n{method} {endpoint}:")
                    print(f"  Response: {response}")
        
        # Exit code
        sys.exit(0 if passed == total else 1)
        
    except KeyboardInterrupt:
        print(f"\n{FAIL} Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{BOMB} Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Always cleanup backend if we started it
        if smoke_test:
            smoke_test.cleanup_backend()
        # Ensure stdout is flushed
        sys.stdout.flush()


if __name__ == "__main__":
    main()

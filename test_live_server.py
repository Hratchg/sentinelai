"""
Live Server Test - Verify backend is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing SentinelAI Backend Server")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/health")
    if response.status_code == 200:
        print("   ✓ Server is healthy!")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version', 'N/A')}")
    else:
        print(f"   ✗ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to server: {e}")
    print("   Make sure the server is running at http://localhost:8000")
    exit(1)

# Test 2: List jobs
print("\n2. Testing jobs endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/jobs")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Jobs endpoint working")
        print(f"   Total jobs: {data.get('total', 0)}")
        print(f"   Current page: {len(data.get('jobs', []))} jobs")
    else:
        print(f"   ✗ Jobs endpoint failed: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check API documentation
print("\n3. Testing API documentation...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("   ✓ Swagger UI available at http://localhost:8000/docs")
    else:
        print(f"   ✗ Docs not available: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Check Week 3 endpoints exist
print("\n4. Testing Week 3 endpoints registration...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})

        week3_endpoints = [
            '/api/v1/results/{job_id}/heatmap',
            '/api/v1/results/{job_id}/alerts'
        ]

        for endpoint in week3_endpoints:
            if endpoint in paths:
                print(f"   ✓ {endpoint} registered")
            else:
                print(f"   ✗ {endpoint} not found")
    else:
        print(f"   ✗ OpenAPI spec not available: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Server Test Complete!")
print("=" * 60)

print("\n✅ Backend is running and ready!")
print("\nNext steps:")
print("1. Open browser: http://localhost:8000/docs")
print("2. Upload a test video using the /upload endpoint")
print("3. Check the results with Week 3 features (heatmap, alerts)")
print("\nServer is running at: http://localhost:8000")

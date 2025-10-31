#!/bin/bash
# Validation script for fullstack example - runs inside Docker network
# This tests the actual production scenario with proper DNS resolution

set -e

DOMAIN="${1:-fullstack-test.local}"
PROJECT_SLUG="${2:-fullstack-test-local-1}"

echo "🔍 Validating Full Stack deployment: $DOMAIN"
echo "Project slug: $PROJECT_SLUG"
echo ""

# Wait for services to be ready (backend needs time to install Flask)
echo "⏳ Waiting for services to start..."
echo "   (Backend: installing Flask + dependencies...)"
sleep 35

# Test 1: Frontend (HTML)
echo "1. Testing frontend (/)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://${PROJECT_SLUG}-frontend-1/" || echo "000")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q "Full Stack"; then
    echo "   ✅ Frontend works (200, contains 'Full Stack')"
else
    echo "   ❌ Frontend failed: HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi

# Test 2: Backend direct (internal Docker network)
echo "2. Testing backend directly (/message)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://${PROJECT_SLUG}-backend-1:8000/message" || echo "000")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q "Hello from Backend"; then
    echo "   ✅ Backend works (200, contains 'Hello from Backend')"
else
    echo "   ❌ Backend failed: HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi

# Test 3: Backend via nginx proxy (/api/message)
echo "3. Testing backend via nginx proxy (/api/message)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://${PROJECT_SLUG}-frontend-1/api/message" || echo "000")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q "Hello from Backend"; then
    echo "   ✅ Nginx proxy works (200, proxied to backend)"
else
    echo "   ❌ Nginx proxy failed: HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi

# Test 4: Backend health via proxy
echo "4. Testing backend health via proxy (/api/health)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://${PROJECT_SLUG}-frontend-1/api/health" || echo "000")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q "healthy"; then
    echo "   ✅ Health endpoint works (200, status: healthy)"
else
    echo "   ❌ Health check failed: HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi

echo ""
echo "✅ All Full Stack tests passed!"
echo "   - Frontend serving HTML ✓"
echo "   - Backend API responding ✓"
echo "   - Nginx proxy working ✓"
echo "   - Health check working ✓"
echo ""
echo "🎉 Full Stack example is production-ready!"


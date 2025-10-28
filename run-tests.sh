#!/bin/bash
set -e

echo "🧪 Running DockLite Tests"
echo "========================="
echo ""

# Backend tests
echo "📦 Backend Tests (pytest)"
echo "-------------------------"
cd /home/pavel/docklite/backend
if command -v pytest &> /dev/null; then
    pytest -v --tb=short
    BACKEND_EXIT=$?
else
    echo "⚠️  pytest not found. Install with: pip install -r requirements.txt"
    BACKEND_EXIT=1
fi
echo ""

# Frontend tests
echo "🎨 Frontend Tests (vitest)"
echo "-------------------------"
cd /home/pavel/docklite/frontend
if [ -d "node_modules" ]; then
    npm test
    FRONTEND_EXIT=$?
else
    echo "⚠️  node_modules not found. Install with: npm install"
    FRONTEND_EXIT=1
fi
echo ""

# Summary
echo "========================="
echo "📊 Test Summary"
echo "========================="
if [ $BACKEND_EXIT -eq 0 ]; then
    echo "✅ Backend tests: PASSED"
else
    echo "❌ Backend tests: FAILED"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ Frontend tests: PASSED"
else
    echo "❌ Frontend tests: FAILED"
fi
echo ""

# Exit with error if any tests failed
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    exit 1
fi

echo "🎉 All tests passed!"
exit 0


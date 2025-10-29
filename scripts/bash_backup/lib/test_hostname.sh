#!/bin/bash
# Test script for hostname functions in common.sh
# Run: bash scripts/lib/test_hostname.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Source common.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Test helper
assert_equals() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
    fi
}

echo "Testing hostname functions..."
echo ""

# Test 1: get_hostname returns something
result=$(get_hostname)
if [ -n "$result" ]; then
    echo -e "${GREEN}✓${NC} get_hostname returns non-empty value: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_hostname returns empty value"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 2: get_access_url basic
result=$(get_access_url)
if [[ "$result" =~ ^http:// ]]; then
    echo -e "${GREEN}✓${NC} get_access_url returns HTTP URL: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_access_url doesn't return HTTP URL"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 3: get_access_url with path
result=$(get_access_url "/api")
if [[ "$result" =~ /api$ ]]; then
    echo -e "${GREEN}✓${NC} get_access_url with path: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_access_url with path failed: $result"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 4: get_access_url with port
result=$(get_access_url "" "8888")
if [[ "$result" =~ :8888$ ]]; then
    echo -e "${GREEN}✓${NC} get_access_url with port: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_access_url with port failed: $result"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 5: get_access_url with path and port
result=$(get_access_url "/dashboard" "8888")
if [[ "$result" =~ :8888/dashboard$ ]]; then
    echo -e "${GREEN}✓${NC} get_access_url with path and port: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_access_url with path and port failed: $result"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 6: get_access_url without port 80
result=$(get_access_url "" "80")
if [[ ! "$result" =~ :80$ ]]; then
    echo -e "${GREEN}✓${NC} get_access_url hides port 80: $result"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗${NC} get_access_url should hide port 80: $result"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Summary
echo ""
echo "=========================================="
if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}All tests passed!${NC} ($TESTS_PASSED/$TESTS_RUN)"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC} ($TESTS_PASSED/$TESTS_RUN passed)"
    exit 1
fi


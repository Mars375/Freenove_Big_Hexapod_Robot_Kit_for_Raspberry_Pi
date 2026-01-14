#!/bin/bash
BASE_URL="http://localhost:8000"

echo "🌐 TEST API ENDPOINTS"
echo "=" | head -c 50 && echo

endpoints=(
    "GET /health"
    "GET /api/status"
    "GET /api/sensors/battery"
    "GET /api/sensors/ultrasonic"
    "POST /api/movement/forward"
    "POST /api/movement/stop"
)

for endpoint in "${endpoints[@]}"; do
    method=$(echo $endpoint | awk '{print $1}')
    path=$(echo $endpoint | awk '{print $2}')
    
    echo -n "Testing $endpoint ... "
    
    if [ "$method" = "GET" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$path")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL$path" -H "Content-Type: application/json" -d '{"speed":50}')
    fi
    
    if [ "$status" = "200" ]; then
        echo "✅ OK ($status)"
    else
        echo "❌ FAIL ($status)"
    fi
done

#!/bin/bash

BASE_URL="http://localhost:5000"

ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/view-current-weather?city=Boston")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Service is healthy."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response_body" | jq .
    fi
  else
    echo "Health check failed. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to create an account
create_account() {
  echo "Creating account..."
  response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d '{"username": "test_user", "password": "test_pass"}')
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 201 ]; then
    echo "Account created successfully."
  else
    echo "Failed to create account. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to log in
login() {
  echo "Logging in..."
  response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username": "test_user", "password": "test_pass"}')
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Login successful."
  else
    echo "Login failed. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to get snack locations
get_snack_location() {
  echo "Getting snack locations for city: Boston..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/get-snack-location?city=Boston")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Snack locations retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to retrieve snack locations. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to get snack recommendations
get_snack_recommendation() {
  echo "Getting snack recommendations for city: Boston..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/get-snack-recommendation?city=Boston")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Snack recommendations retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to retrieve snack recommendations. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to get snack pairing
get_snack_pairing() {
  echo "Getting snack pairing for city: Boston..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/get-snack-pairing?city=Boston")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Snack pairing retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to retrieve snack pairing. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Run smoketest
check_health
create_account
login
get_snack_location
get_snack_recommendation
get_snack_pairing

echo "Smoketest completed successfully!"
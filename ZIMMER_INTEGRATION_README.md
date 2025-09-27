# Zimmer Automation Integration

This document provides curl examples for testing the Zimmer integration endpoints.

## Environment Variables

Set these environment variables before testing:

```bash
export BASE="https://your-domain.com"
export TOKEN="your-zimmer-service-token"
```

## Ops Curls

### 1. Health Check (Public)

```bash
curl -X GET "$BASE/health"
```

### 2. Provision Tenant (Protected)

```bash
curl -X POST "$BASE/api/zimmer/provision" \
  -H "Content-Type: application/json" \
  -H "X-Zimmer-Service-Token: $TOKEN" \
  -d '{
    "user_automation_id": 123,
    "user_id": 456,
    "demo_tokens": 1000,
    "service_url": "https://example.com"
  }'
```

### 3. Consume Usage (Protected)

```bash
curl -X POST "$BASE/api/zimmer/usage/consume" \
  -H "Content-Type: application/json" \
  -H "X-Zimmer-Service-Token: $TOKEN" \
  -d '{
    "user_automation_id": 123,
    "units": 10,
    "usage_type": "chat",
    "meta": {"conversation_id": "test123"}
  }'
```

### 4. KB Status (Protected)

```bash
curl -X GET "$BASE/api/zimmer/kb/status?user_automation_id=123" \
  -H "X-Zimmer-Service-Token: $TOKEN"
```

### 5. KB Reset (Protected)

```bash
curl -X POST "$BASE/api/zimmer/kb/reset?user_automation_id=123" \
  -H "X-Zimmer-Service-Token: $TOKEN"
```

### 6. Chat API (Expected latency < 9-10s)

```bash
curl -X POST "$BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test123",
    "message": "سلام"
  }'
```

## Endpoints

### 1. Public Health Check

```bash
curl -X GET "${BASE_URL}/health" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "abc1234",
  "uptime": 3600
}
```

### 2. Provision Tenant (Protected)

```bash
curl -X POST "${BASE_URL}/api/zimmer/provision" \
  -H "Content-Type: application/json" \
  -H "X-Zimmer-Service-Token: ${ZIMMER_SERVICE_TOKEN}" \
  -d '{
    "user_automation_id": 123,
    "user_id": 456,
    "demo_tokens": 1000,
    "service_url": "https://example.com"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Tenant provisioned successfully",
  "provisioned_at": "2024-01-01T12:00:00",
  "integration_status": "active",
  "service_url": "https://example.com"
}
```

### 3. Consume Usage (Protected)

```bash
curl -X POST "${BASE_URL}/api/zimmer/usage/consume" \
  -H "Content-Type: application/json" \
  -H "X-Zimmer-Service-Token: ${ZIMMER_SERVICE_TOKEN}" \
  -d '{
    "user_automation_id": 123,
    "units": 10,
    "usage_type": "chat",
    "meta": {"conversation_id": "test123"}
  }'
```

**Expected Response:**
```json
{
  "accepted": true,
  "remaining_demo_tokens": 990,
  "remaining_paid_tokens": 0,
  "message": "Usage consumed successfully"
}
```

### 4. KB Status (Protected)

```bash
curl -X GET "${BASE_URL}/api/zimmer/kb/status?user_automation_id=123" \
  -H "X-Zimmer-Service-Token: ${ZIMMER_SERVICE_TOKEN}"
```

**Expected Response:**
```json
{
  "status": "empty",
  "last_updated": null,
  "total_documents": 0,
  "healthy": false
}
```

### 5. KB Reset (Protected)

```bash
curl -X POST "${BASE_URL}/api/zimmer/kb/reset?user_automation_id=123" \
  -H "X-Zimmer-Service-Token: ${ZIMMER_SERVICE_TOKEN}"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Knowledge base reset successfully",
  "reset_at": "2024-01-01T12:00:00"
}
```

## Authentication Testing

### Test Missing Token (Should return 401)

```bash
curl -X GET "${BASE_URL}/api/zimmer/kb/status?user_automation_id=123"
```

### Test Wrong Token (Should return 401)

```bash
curl -X GET "${BASE_URL}/api/zimmer/kb/status?user_automation_id=123" \
  -H "X-Zimmer-Service-Token: wrong-token"
```

## Chat API Timeout Test

```bash
curl -X POST "${BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test123",
    "message": "سلام"
  }'
```

**Expected:** Response within 9 seconds with valid JSON.

## Configuration

The following environment variables control the integration:

- `ZIMMER_SERVICE_TOKEN`: Required for authentication
- `CHAT_BUDGET_SECONDS`: Chat timeout budget (default: 8)
- `CHAT_API_TIMEOUT`: Maximum chat API timeout (default: 9)

## Database Schema

The integration adds a `zimmer_tenants` table with the following fields:

- `user_automation_id`: Unique identifier for the automation
- `user_id`: User identifier
- `integration_status`: Status of the integration
- `service_url`: Optional service URL
- `demo_tokens`: Available demo tokens
- `paid_tokens`: Available paid tokens
- `kb_status`: Knowledge base status
- `kb_last_updated`: Last KB update timestamp
- `kb_total_documents`: Number of documents in KB
- `kb_healthy`: KB health status

## Logging

All Zimmer endpoints log:
- Method and path
- Response status
- Latency in milliseconds
- User automation ID (when applicable)

Logs do not include sensitive data like tokens or request bodies.

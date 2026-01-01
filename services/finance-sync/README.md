# Finance Sync Service

Monobank API integration for real-time financial data synchronization.

## Overview

This service provides:
- Real-time transaction synchronization from Monobank Personal API
- Webhook-based push notifications for transactions
- Statement data persistence and querying
- REST API for accessing synchronized financial data

## Architecture

```
Monobank API (external.monobank-api)
  |
  +----> (sync-call) Finance Sync Service (svc.finance-sync)
  |                     |
  |                     +----> (dependency) Accounting Storage (db.accounting)
  |
  +----> (webhook) Finance Sync Service
                     |
                     +----> (dependency) Accounting Storage
```

## Integration Points

### Pull: /personal/statement
- Endpoint: `GET https://api.monobank.ua/personal/statement/{account}/{from}/{to}`
- Headers: `X-Token: {personal-token}`
- Frequency: Configurable (default: 1 request per 60 seconds)

### Push: Webhook
- Endpoint: `POST https://your-domain/mono/webhook`
- Validates webhook signature
- Updates transaction data in real-time

## Setup

1. Get personal token from https://api.monobank.ua
2. Set `MONO_TOKEN` in `.env`
3. Configure webhook URL
4. Start service: `python main.py`

## API

### GET /health
Service health check

### GET /statements?limit=10
Recent transactions

### GET /client-info
Client information

## Environment Variables

```
MONO_TOKEN=your_token_here
MONO_API_BASE=https://api.monobank.ua
WEBHOOK_URL=https://your-domain/mono/webhook
DB_PATH=./data/accounting.db
```

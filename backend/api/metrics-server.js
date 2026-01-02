// Bakhmach Business Hub - Metrics REST API Server
// Real-time metrics API for visualizations

const express = require('express');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const prometheus = require('prom-client');
const WebSocket = require('ws');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(compression());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP'
});
app.use('/api/', limiter);

// Prometheus metrics
const register = new prometheus.Registry();
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

// Mock data store
const metricsStore = {
  arr: 285000,
  activeUsers: 8243,
  marketPenetration: 0.44,
  churnRate: 2.1,
  timestamp: Date.now()
};

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// GET all metrics
app.get('/api/metrics', (req, res) => {
  const timer = httpRequestDuration.startTimer();
  res.json({
    arr: metricsStore.arr,
    activeUsers: metricsStore.activeUsers,
    marketPenetration: metricsStore.marketPenetration,
    churnRate: metricsStore.churnRate,
    timestamp: metricsStore.timestamp,
    trends: {
      arrGrowth: 45,
      userGrowth: 32,
      churnImprovement: 0.3
    }
  });
  timer({ method: 'GET', route: '/api/metrics', status_code: 200 });
});

// GET specific metric
app.get('/api/metrics/:metric', (req, res) => {
  const timer = httpRequestDuration.startTimer();
  const { metric } = req.params;
  
  if (metricsStore[metric]) {
    res.json({
      metric,
      value: metricsStore[metric],
      timestamp: metricsStore.timestamp
    });
    timer({ method: 'GET', route: `/api/metrics/${metric}`, status_code: 200 });
  } else {
    res.status(404).json({ error: 'Metric not found' });
    timer({ method: 'GET', route: `/api/metrics/${metric}`, status_code: 404 });
  }
});

// POST update metric
app.post('/api/metrics/:metric', (req, res) => {
  const timer = httpRequestDuration.startTimer();
  const { metric } = req.params;
  const { value } = req.body;
  
  if (metricsStore.hasOwnProperty(metric)) {
    metricsStore[metric] = value;
    metricsStore.timestamp = Date.now();
    res.json({
      success: true,
      metric,
      newValue: value,
      timestamp: metricsStore.timestamp
    });
    timer({ method: 'POST', route: `/api/metrics/${metric}`, status_code: 200 });
    
    // Broadcast to WebSocket clients
    broadcastUpdate({ metric, value });
  } else {
    res.status(400).json({ error: 'Invalid metric' });
    timer({ method: 'POST', route: `/api/metrics/${metric}`, status_code: 400 });
  }
});

// WebSocket for real-time updates
const wss = new WebSocket.Server({ noServer: true });
const clients = new Set();

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  clients.add(ws);
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
    } catch (e) {
      console.error('Invalid message:', e);
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
    clients.delete(ws);
  });
});

function broadcastUpdate(data) {
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({
        type: 'metric_update',
        data,
        timestamp: new Date().toISOString()
      }));
    }
  });
}

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
});

// Start server
const server = app.listen(port, () => {
  console.log(`🚀 Metrics API Server running on port ${port}`);
  console.log(`📈 Health check: http://localhost:${port}/health`);
  console.log(`📊 Metrics API: http://localhost:${port}/api/metrics`);
});

// WebSocket upgrade
server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

module.exports = app;

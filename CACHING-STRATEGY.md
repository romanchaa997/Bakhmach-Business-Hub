# Caching Strategy & Performance Optimization

## Overview
Multi-layer caching strategy for Bakhmach Business Hub covering HTTP caching, database query caching, distributed caching, and CDN optimization.

## Caching Architecture

### 1. HTTP Caching Layer (Browser & CDN)

#### Cache Headers Configuration

```typescript
// Middleware: HTTP cache headers
app.use((req, res, next) => {
  // Static assets: long-term caching
  if (req.path.match(/\.(js|css|png|jpg|gif|woff2?)$/)) {
    res.set('Cache-Control', 'public, max-age=31536000, immutable');
    res.set('ETag', generateETag(file));
  }
  // API responses: short-term caching
  else if (req.path.startsWith('/api/')) {
    res.set('Cache-Control', 'private, max-age=300'); // 5 minutes
    res.set('ETag', generateETag(data));
  }
  // HTML: no cache
  else {
    res.set('Cache-Control', 'no-cache, no-store, must-revalidate');
  }
  next();
});
```

#### Cache Strategies by Content Type

**Static Assets (CSS, JS, Fonts, Images):**
- Cache Duration: 1 year
- Strategy: Content hash in filename for cache busting
- ETag: Yes, for validation
- GZIP: Yes, pre-compressed

**API Responses:**
- Cache Duration: 5-30 minutes (depending on endpoint)
- Strategy: Private cache (user-specific)
- Vary: Accept-Encoding, Authorization
- Cache Key: URL + query params + user ID

**HTML:**
- Cache Duration: No caching
- Strategy: Always fetch fresh
- Reason: Dynamic content updates

### 2. Redis In-Memory Cache

#### Redis Configuration

```yaml
# redis.conf
port: 6379
maxmemory: 2gb
maxmemory-policy: allkeys-lru  # Evict least recently used keys

# Persistence
save 900 1        # Save if 1 key changed in 15 minutes
save 300 10       # Save if 10 keys changed in 5 minutes
save 60 10000     # Save if 10000 keys changed in 1 minute

# Replication
replica-read-only yes
replica-serve-stale-data yes
```

#### Cache Pattern Examples

**User Session Cache:**
```typescript
const sessionTTL = 86400 * 7; // 7 days
await redis.setex(`session:${sessionId}`, sessionTTL, JSON.stringify(sessionData));
```

**Database Query Cache:**
```typescript
const cacheKey = `query:users:${userId}`;
let user = await redis.get(cacheKey);

if (!user) {
  user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour
}
```

**Computed Result Cache:**
```typescript
const reportKey = `report:monthly:${month}`;
let report = await redis.get(reportKey);

if (!report) {
  report = await computeMonthlyReport(month);
  await redis.setex(reportKey, 86400, JSON.stringify(report)); // 1 day
}
```

### 3. Database Query Caching

#### Query Result Caching

```typescript
// Query cache wrapper
class CachedDatabase {
  async query(sql, params, ttl = 3600) {
    const cacheKey = this.getCacheKey(sql, params);
    
    // Try cache first
    const cached = await redis.get(cacheKey);
    if (cached) return JSON.parse(cached);
    
    // Execute query
    const result = await db.execute(sql, params);
    
    // Store in cache
    await redis.setex(cacheKey, ttl, JSON.stringify(result));
    
    return result;
  }
  
  getCacheKey(sql, params) {
    const hash = crypto.createHash('md5')
      .update(sql + JSON.stringify(params))
      .digest('hex');
    return `query:${hash}`;
  }
}
```

#### Database-Level Optimization

```sql
-- Query planning and indexing
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = $1;

-- Index strategy
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category_id, updated_at);
```

### 4. Application-Level Caching

#### Cache Invalidation Patterns

**Time-Based Invalidation:**
```typescript
// Simple TTL expiration
await redis.setex('featured-products', 3600, JSON.stringify(products));
```

**Event-Based Invalidation:**
```typescript
// Invalidate on user profile update
app.post('/api/users/:id', async (req, res) => {
  const user = await updateUser(req.params.id, req.body);
  
  // Invalidate related caches
  await redis.del(`user:${req.params.id}`);
  await redis.del(`user-profile:${req.params.id}`);
  await redis.del('featured-users');
  
  res.json(user);
});
```

**Tag-Based Invalidation:**
```typescript
// Group cache by tags
const cacheKey = 'products:featured';
await redis.setex(cacheKey, 3600, JSON.stringify(products));
await redis.sadd('cache-tag:products', cacheKey);

// Invalidate all product caches
const productCaches = await redis.smembers('cache-tag:products');
await redis.del(...productCaches);
```

### 5. HTTP/2 Push & Server Push

```typescript
// Server push critical resources
app.get('/page', (req, res) => {
  res.push('/css/main.css', {
    'content-type': 'text/css',
    'cache-control': 'public, max-age=31536000'
  });
  
  res.push('/js/app.js', {
    'content-type': 'application/javascript',
    'cache-control': 'public, max-age=31536000'
  });
  
  res.sendFile('index.html');
});
```

### 6. CDN Strategy

#### CloudFront / Cloudflare Configuration

```yaml
# Cache behavior configuration
cache_behaviors:
  - pattern: /static/*
    ttl: 31536000  # 1 year
    compress: true
    headers: 
      - Accept-Encoding
  
  - pattern: /api/*
    ttl: 300  # 5 minutes
    query_strings: true
    headers:
      - Authorization
      - User-Agent
  
  - pattern: /
    ttl: 0  # No caching
```

## Cache Performance Metrics

### Cache Hit Ratio
```
Hit Ratio = Cache Hits / (Cache Hits + Cache Misses)
Target: > 80% for optimal performance
```

### Monitoring

```typescript
// Track cache performance
class CacheMetrics {
  async recordHit(key) {
    await redis.incr(`metrics:cache-hits:${key}`);
  }
  
  async recordMiss(key) {
    await redis.incr(`metrics:cache-misses:${key}`);
  }
  
  async getHitRatio(key) {
    const hits = parseInt(await redis.get(`metrics:cache-hits:${key}`)) || 0;
    const misses = parseInt(await redis.get(`metrics:cache-misses:${key}`)) || 0;
    return hits / (hits + misses);
  }
}
```

## Cache Stampede Prevention

### Lock-Based Approach
```typescript
const lockKey = `lock:${cacheKey}`;
const lockValue = uuid();

// Try to acquire lock
if (await redis.set(lockKey, lockValue, 'NX', 'EX', 10)) {
  try {
    const result = await expensiveQuery();
    await redis.setex(cacheKey, ttl, JSON.stringify(result));
  } finally {
    // Release lock if still owned
    const current = await redis.get(lockKey);
    if (current === lockValue) {
      await redis.del(lockKey);
    }
  }
} else {
  // Wait for lock holder to populate cache
  for (let i = 0; i < 10; i++) {
    const cached = await redis.get(cacheKey);
    if (cached) return JSON.parse(cached);
    await sleep(100);
  }
}
```

## Distributed Cache Invalidation

### Pub/Sub Pattern

```typescript
// Publish cache invalidation
const publishInvalidation = async (key) => {
  await redis.publish('cache-invalidation', JSON.stringify({
    key,
    timestamp: Date.now(),
    server: process.env.SERVER_ID
  }));
};

// Subscribe to invalidations
redis.subscribe('cache-invalidation', (message) => {
  const { key } = JSON.parse(message);
  localCache.delete(key);
});
```

## Cache Implementation Checklist

- [ ] HTTP cache headers configured correctly
- [ ] Redis cluster setup with replication
- [ ] Cache key naming conventions established
- [ ] TTL strategy defined per content type
- [ ] Cache invalidation events implemented
- [ ] Cache metrics monitoring enabled
- [ ] Stampede prevention implemented
- [ ] CDN configured with proper headers
- [ ] Cache hit ratio > 80%
- [ ] Regular cache inspection and cleanup

## Best Practices

1. **Use cache keys that include version numbers**: `user:v1:12345`
2. **Set reasonable TTLs**: Not too short (overhead) or too long (stale)
3. **Implement graceful degradation**: Don't fail if cache is unavailable
4. **Monitor cache memory usage**: Prevent out-of-memory conditions
5. **Use compression**: For large cached objects
6. **Implement cache warming**: Pre-populate frequently accessed data
7. **Version your cache**: Handle schema changes gracefully
8. **Test cache behavior**: Ensure invalidation works properly

## Estimated Performance Improvement

- Page load time: 40-60% faster
- API response time: 70-90% faster  
- Database load: 50-70% reduction
- Bandwidth usage: 30-50% reduction

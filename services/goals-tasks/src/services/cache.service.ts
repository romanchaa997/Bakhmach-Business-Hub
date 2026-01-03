// Cache Service for Goals + Tasks Microservice
// Redis-based caching layer with TTL and invalidation strategies

import Redis from 'ioredis';
import { Logger } from '../utils/logger';

interface CacheOptions {
  ttl?: number; // Time to live in seconds
  prefix?: string;
}

export class CacheService {
  private redis: Redis;
  private logger: Logger;
  private readonly defaultTTL = 3600; // 1 hour
  private readonly defaultPrefix = 'goals-tasks:';

  constructor(redisUrl?: string) {
    this.logger = Logger.getInstance();
    
    try {
      this.redis = new Redis(redisUrl || process.env.REDIS_URL || 'redis://localhost:6379');
      
      this.redis.on('connect', () => {
        this.logger.info('Cache service connected to Redis');
      });
      
      this.redis.on('error', (err) => {
        this.logger.error('Redis connection error:', err);
      });
    } catch (error) {
      this.logger.error('Failed to initialize cache service:', error);
      throw error;
    }
  }

  /**
   * Get value from cache
   */
  public async get<T>(key: string): Promise<T | null> {
    try {
      const fullKey = this.buildKey(key);
      const value = await this.redis.get(fullKey);
      
      if (!value) {
        return null;
      }
      
      return JSON.parse(value) as T;
    } catch (error) {
      this.logger.warn(`Cache get error for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Set value in cache
   */
  public async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    try {
      const fullKey = this.buildKey(key);
      const serialized = JSON.stringify(value);
      const expiry = ttl || this.defaultTTL;
      
      await this.redis.setex(fullKey, expiry, serialized);
      
      this.logger.debug(`Cache set: ${key} with TTL ${expiry}s`);
    } catch (error) {
      this.logger.warn(`Cache set error for key ${key}:`, error);
    }
  }

  /**
   * Delete value from cache
   */
  public async del(key: string): Promise<boolean> {
    try {
      const fullKey = this.buildKey(key);
      const result = await this.redis.del(fullKey);
      
      this.logger.debug(`Cache deleted: ${key}`);
      return result > 0;
    } catch (error) {
      this.logger.warn(`Cache delete error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Delete multiple keys matching a pattern
   */
  public async delPattern(pattern: string): Promise<number> {
    try {
      const fullPattern = this.buildKey(pattern);
      const keys = await this.redis.keys(fullPattern);
      
      if (keys.length === 0) {
        return 0;
      }
      
      const result = await this.redis.del(...keys);
      
      this.logger.debug(`Cache deleted ${result} keys matching pattern: ${pattern}`);
      return result;
    } catch (error) {
      this.logger.warn(`Cache delete pattern error for ${pattern}:`, error);
      return 0;
    }
  }

  /**
   * Check if key exists
   */
  public async exists(key: string): Promise<boolean> {
    try {
      const fullKey = this.buildKey(key);
      const result = await this.redis.exists(fullKey);
      return result === 1;
    } catch (error) {
      this.logger.warn(`Cache exists error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Get or set cache (cache-aside pattern)
   */
  public async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    try {
      // Try to get from cache
      const cached = await this.get<T>(key);
      if (cached) {
        this.logger.debug(`Cache hit: ${key}`);
        return cached;
      }

      // Cache miss - fetch from source
      this.logger.debug(`Cache miss: ${key}`);
      const value = await fetcher();
      
      // Store in cache
      await this.set(key, value, ttl);
      
      return value;
    } catch (error) {
      this.logger.error(`GetOrSet error for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Increment counter
   */
  public async increment(key: string, amount: number = 1): Promise<number> {
    try {
      const fullKey = this.buildKey(key);
      const result = await this.redis.incrby(fullKey, amount);
      return result;
    } catch (error) {
      this.logger.warn(`Cache increment error for key ${key}:`, error);
      return 0;
    }
  }

  /**
   * Set expiry on existing key
   */
  public async expire(key: string, ttl: number): Promise<boolean> {
    try {
      const fullKey = this.buildKey(key);
      const result = await this.redis.expire(fullKey, ttl);
      return result === 1;
    } catch (error) {
      this.logger.warn(`Cache expire error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Clear all cache
   */
  public async clear(): Promise<void> {
    try {
      const pattern = this.buildKey('*');
      const keys = await this.redis.keys(pattern);
      
      if (keys.length > 0) {
        await this.redis.del(...keys);
        this.logger.info(`Cache cleared: ${keys.length} keys deleted`);
      }
    } catch (error) {
      this.logger.warn('Cache clear error:', error);
    }
  }

  /**
   * Get cache statistics
   */
  public async getStats(): Promise<Record<string, any>> {
    try {
      const info = await this.redis.info('stats');
      return { redis_info: info };
    } catch (error) {
      this.logger.warn('Failed to get cache stats:', error);
      return {};
    }
  }

  /**
   * Health check
   */
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.redis.ping();
      return response === 'PONG';
    } catch (error) {
      this.logger.error('Cache health check failed:', error);
      return false;
    }
  }

  /**
   * Close connection
   */
  public async close(): Promise<void> {
    try {
      await this.redis.quit();
      this.logger.info('Cache service connection closed');
    } catch (error) {
      this.logger.error('Error closing cache service:', error);
    }
  }

  private buildKey(key: string): string {
    return `${this.defaultPrefix}${key}`;
  }
}

// Singleton instance
let cacheServiceInstance: CacheService | null = null;

export function getCacheService(): CacheService {
  if (!cacheServiceInstance) {
    cacheServiceInstance = new CacheService();
  }
  return cacheServiceInstance;
}

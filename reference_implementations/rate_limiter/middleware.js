const Redis = require("ioredis");

// Load configuration from environment variables
const REDIS_URL = process.env.REDIS_URL || "redis://127.0.0.1:6379";
const redis = new Redis(REDIS_URL);

// Sliding Window Algorithm using an Atomic Lua Script
// KEYS[1] = Rate limit key (e.g., rate_limit:user:123)
// ARGV[1] = Current timestamp (in milliseconds)
// ARGV[2] = Window size (in milliseconds)
// ARGV[3] = Request limit
// Returns: [current_count, remaining_ttl_in_ms]
const SLIDING_WINDOW_SCRIPT = `
  local key = KEYS[1]
  local now = tonumber(ARGV[1])
  local window = tonumber(ARGV[2])
  local limit = tonumber(ARGV[3])
  local clearBefore = now - window

  -- Remove requests older than the sliding window
  redis.call('ZREMRANGEBYSCORE', key, 0, clearBefore)

  -- Count current requests in the window
  local count = redis.call('ZCARD', key)

  -- If limit exceeded, return the count without adding
  if count >= limit then
    -- TTL logic (rough estimation of when the oldest request expires)
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local ttl = window
    if oldest and oldest[2] then
       ttl = tonumber(oldest[2]) + window - now
    end
    return {count + 1, ttl}
  end

  -- Add the new request
  -- We use 'now' + random payload as member to avoid collisions
  redis.call('ZADD', key, now, now .. '-' .. math.random(10000))
  
  -- Update the expiration for the entire key to prevent memory leaks
  redis.call('PEXPIRE', key, window)

  return {count + 1, window}
`;

// Register the Lua script in Redis
redis.defineCommand("slidingWindowRateLimit", {
  numberOfKeys: 1,
  lua: SLIDING_WINDOW_SCRIPT,
});

/**
 * Tier definitions
 */
const TIERS = {
  Free: { limit: 100, windowSeconds: 60 },
  Pro: { limit: 1000, windowSeconds: 60 },
  Enterprise: { limit: parseInt(process.env.ENTERPRISE_LIMIT) || 10000, windowSeconds: 60 }
};

/**
 * Express Middleware for Production Rate Limiting
 */
const rateLimiter = async (req, res, next) => {
  try {
    // 1. Identify Client and Tier
    const apiKey = req.headers['x-api-key'];
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    
    // Fallback to Free tier if no API key provided (or IP based)
    const identifier = apiKey ? `apikey:${apiKey}` : `ip:${ip}`;
    const userTier = req.user?.tier || 'Free'; // Extracted via prior auth middleware
    
    const tierConfig = TIERS[userTier];
    if (!tierConfig) {
      return res.status(400).json({ error: { message: "Invalid subscription tier" }});
    }

    const { limit, windowSeconds } = tierConfig;
    const windowMs = windowSeconds * 1000;
    const key = `rate_limit:${identifier}`;
    const nowMs = Date.now();

    // 2. Execute Atomic Redis Script
    // Using atomic Lua ensures zero race conditions across distributed instances
    const [currentCount, ttlMs] = await redis.slidingWindowRateLimit(
      key, 
      nowMs, 
      windowMs, 
      limit
    );

    // 3. Calculate Headers
    const remaining = Math.max(0, limit - currentCount);
    const resetTimeEpoch = Math.ceil((nowMs + ttlMs) / 1000);

    res.set({
      "X-RateLimit-Limit": limit,
      "X-RateLimit-Remaining": remaining,
      "X-RateLimit-Reset": resetTimeEpoch,
    });

    // 4. Enforce Limit
    if (currentCount > limit) {
      const retryAfterSeconds = Math.ceil(ttlMs / 1000);
      res.set("Retry-After", retryAfterSeconds);

      return res.status(429).json({
        error: {
          code: "RATE_LIMIT_EXCEEDED",
          message: "You have exceeded your rate limit.",
          retry_after: retryAfterSeconds
        }
      });
    }

    next();
  } catch (error) {
    console.error("Rate Limiter Error:", error);
    // Production Best Practice: Fail-Open to prevent blocking traffic during Redis outages
    if (process.env.RATE_LIMIT_FAIL_OPEN === "true") {
      return next(); 
    }
    return res.status(500).json({ error: { message: "Internal Server Error" }});
  }
};

module.exports = { rateLimiter, redis, TIERS };

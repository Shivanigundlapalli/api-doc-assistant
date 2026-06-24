const { rateLimiter, redis } = require('./middleware');

// Mock Express req, res, next
const mockReq = (overrides = {}) => ({
  headers: {
    'x-api-key': 'test_key_123'
  },
  socket: {
    remoteAddress: '127.0.0.1'
  },
  user: {
    tier: 'Free'
  },
  ...overrides
});

const mockRes = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  res.set = jest.fn();
  return res;
};

const mockNext = jest.fn();

describe('Rate Limiter Middleware', () => {
  beforeEach(async () => {
    // Clear redis before each test
    await redis.flushall();
    jest.clearAllMocks();
  });

  afterAll(async () => {
    await redis.quit();
  });

  it('should allow requests under the limit and set headers', async () => {
    const req = mockReq();
    const res = mockRes();

    await rateLimiter(req, res, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(res.set).toHaveBeenCalledWith(expect.objectContaining({
      'X-RateLimit-Limit': 100,
      'X-RateLimit-Remaining': 99,
      'X-RateLimit-Reset': expect.any(Number)
    }));
  });

  it('should block requests over the limit and set Retry-After', async () => {
    const req = mockReq();
    
    // Simulate 100 fast requests
    for (let i = 0; i < 100; i++) {
      const res = mockRes();
      await rateLimiter(req, res, jest.fn());
    }

    // The 101st request should be blocked
    const resBlocked = mockRes();
    await rateLimiter(req, resBlocked, mockNext);

    expect(mockNext).not.toHaveBeenCalled();
    expect(resBlocked.status).toHaveBeenCalledWith(429);
    expect(resBlocked.json).toHaveBeenCalledWith(expect.objectContaining({
      error: expect.objectContaining({
        code: 'RATE_LIMIT_EXCEEDED'
      })
    }));
    expect(resBlocked.set).toHaveBeenCalledWith('Retry-After', expect.any(Number));
  });

  it('should apply higher limits for Pro users', async () => {
    const req = mockReq({ user: { tier: 'Pro' } });
    const res = mockRes();

    await rateLimiter(req, res, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(res.set).toHaveBeenCalledWith(expect.objectContaining({
      'X-RateLimit-Limit': 1000,
      'X-RateLimit-Remaining': 999
    }));
  });

  it('should fail-open if Redis crashes and ENV allows it', async () => {
    process.env.RATE_LIMIT_FAIL_OPEN = 'true';
    
    // Break redis temporarily
    const originalScript = redis.slidingWindowRateLimit;
    redis.slidingWindowRateLimit = jest.fn().mockRejectedValue(new Error('Redis Down'));

    const req = mockReq();
    const res = mockRes();

    await rateLimiter(req, res, mockNext);

    expect(mockNext).toHaveBeenCalled(); // Traffic allowed through

    // Restore
    redis.slidingWindowRateLimit = originalScript;
    delete process.env.RATE_LIMIT_FAIL_OPEN;
  });
});

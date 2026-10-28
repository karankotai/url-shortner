# URL Shortener - System Design Document

## Architecture Overview

- **Components**: FastAPI (API layer), PostgreSQL (persistent storage), Redis (cache layer)
- **Pattern**: Cache-aside (lazy-loading) for read-heavy optimization
- **Encoding**: Base62 from auto-increment database IDs for short code generation

## Trade-offs

## cache-miss handling
- The first request to a short code will hit the database to fetch the original URL.
- Subsequent requests will hit the cache, saving database load.

### 302 vs 301 Redirects
- We chose 302 (temporary redirect) because browsers don't cache it.
- This means every visit hits our server, letting us track click analytics.
- 301 (permanent redirect) would be faster for repeat visitors but we'd lose visibility.

### Cache TTL (1 hour)
- Short enough that deleted/updated URLs become unreachable within an hour.
- Long enough that popular links stay cached through traffic spikes.
- Trade-off: stale cache for up to 1 hour vs database load from frequent cache misses.

### Base62 Encoding vs Hashing
- Base62 from sequential IDs is collision-free by design.
- Hashing (MD5/SHA-256 + truncation) introduces collision risk requiring resolution logic.
- Trade-off: Base62 is simpler and faster, but codes are predictable (sequential).

## Scaling Strategies

### If reads increase (more redirects)
- Add Redis replicas for read scaling.
- Introduce a CDN layer for the most popular short codes.

### If writes increase (more shortening requests)
- Partition the database by ID range.
- Pre-generate short code batches to avoid sequential bottlenecks.

### If the system goes global
- Deploy to multiple regions with a shared database or eventual consistency.
- Use a distributed ID generator (like Snowflake) instead of auto-increment.

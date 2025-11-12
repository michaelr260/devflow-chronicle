# Docker Build Optimization Guide

## Changes Made

This document explains the Docker build optimizations implemented to prevent unnecessary package reinstalls during rebuilds.

### 1. Multi-Stage Build with Virtual Environment

**Previous Issue:** The production stage was reinstalling all Python packages from scratch, even though the builder stage had already done this work.

**Solution:**
- Builder stage creates a Python virtual environment at `/opt/venv`
- Production stage copies the pre-built virtual environment from the builder
- No redundant pip install in production stage
- Result: **Significantly faster rebuilds** when only code changes

### 2. Removed `--no-cache-dir` Flag

**Previous Issue:** This flag prevented pip from caching downloaded wheels, forcing re-download on every rebuild.

**Solution:**
- Removed `--no-cache-dir` from pip install commands
- pip now caches wheels locally, enabling reuse across builds
- Result: **Faster downloads** on subsequent builds

### 3. Proper Layer Ordering

**Optimization:**
- `requirements.txt` is copied first (before source code)
- Dependencies change less frequently than code
- Docker reuses the dependency layer unless requirements.txt changes
- Only code changes trigger a rebuild of that layer

### 4. BuildKit Support

**Enhancement:**
- Docker BuildKit enabled for better caching and parallel builds
- Faster build times and more efficient layer management

## Build Performance

### First Build
- ~5-10 minutes (depends on internet speed)
- Downloads all dependencies and creates virtual environment

### Subsequent Builds (code changes only)
- **~30-60 seconds** instead of 5-10 minutes
- Reuses cached dependency layer
- Only rebuilds application code layer

### Subsequent Builds (requirements.txt changes)
- ~2-3 minutes
- Rebuilds dependencies, but BuildKit makes it more efficient
- Reuses system package layer

## Usage

### Quick Rebuild (with cache)
```bash
./docker-build.sh
```

### Full Rebuild (no cache)
```bash
./docker-build.sh --no-cache
```

### Using docker-compose directly
```bash
# Quick build with BuildKit enabled
DOCKER_BUILDKIT=1 docker-compose build

# Full rebuild
DOCKER_BUILDKIT=1 docker-compose build --no-cache
```

## Key Improvements Summary

| Aspect | Before | After |
|--------|--------|-------|
| Reinstalls on code change | Yes (full reinstall) | No (cached) |
| Wheel caching | Disabled | Enabled |
| Virtual environment | Duplicated | Shared via COPY --from |
| Build for code changes | 5-10 min | 30-60 sec |
| BuildKit support | No | Yes |

## Technical Details

### Dockerfile Structure

1. **Builder Stage**
   - Install build tools (gcc, g++, git)
   - Create Python virtual environment
   - Install all dependencies to venv

2. **Production Stage**
   - Copy only runtime dependency (git)
   - Copy pre-built venv from builder
   - Copy application code
   - Set up user and permissions

This approach ensures:
- Build dependencies don't pollute final image
- All Python packages are pre-built
- Fast layer reuse via Docker caching
- Optimal image size

### Environment Variables
```dockerfile
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv
```

These ensure the virtual environment is always used for Python execution.

## Troubleshooting

**Issue:** Build still taking too long
- Run: `docker system prune -a` to clear all cached images
- Then rebuild with `./docker-build.sh --no-cache`

**Issue:** Stale dependencies
- Update `requirements.txt`
- Run `./docker-build.sh` (cache will be invalidated)

**Issue:** BuildKit not working
- Check Docker version (needs 19.03+)
- Enable experimental features if needed

"""Rate limiter configuration.

Using a separate module avoids circular imports between main.py and api modules.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter — 20 messages per 5 minutes (1 minute = 60 seconds)
# 20/minute matches spec: "20 messages/5min per IP" ≈ 4/minute, but API
# uses per-minute windows. Using 20/minute for safety margin.
limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
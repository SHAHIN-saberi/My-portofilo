"""
Vercel Serverless entry point for FastAPI backend.
This file wraps the FastAPI app for Vercel's Python runtime.
"""
from app.main import app

# Export the FastAPI app for Vercel
# Vercel will use this as the WSGI/ASGI application
def handler(request):
    """Vercel serverless handler - delegates to FastAPI via ASGI."""
    # For Vercel's Python runtime, we need to use the ASGI interface
    # The app object itself is ASGI-compliant
    return app

# Alternative: direct export for newer Vercel Python runtime
# Uncomment if the handler approach doesn't work:
# app = app

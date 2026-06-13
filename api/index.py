# Vercel entry point — imports the FastAPI app from app/server.py
# NOTE: SSE streaming endpoints (/api/run/stream, /api/orchestrate/stream) work
# but Vercel serverless functions have a 60-second hard timeout.
# For long-running orchestrations, keep the API on Railway or Render instead.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.server import app  # noqa: F401  (Vercel looks for `app`)

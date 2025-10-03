# gunicorn.conf.py — XMRT Ecosystem / Render-ready
# - Binds to $PORT
# - Foreground (no daemon)
# - Uses gthread (no extra deps like gevent)
# - Boots coordination core + optional autonomous worker after fork

import os
import multiprocessing

# -----------------------------
# Core server binding / backlog
# -----------------------------
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = int(os.environ.get("GUNICORN_BACKLOG", "2048"))

# -----------------------------
# Worker model & concurrency
# -----------------------------
# Use threads worker (built-in) to avoid extra deps.
worker_class = "gthread"
workers = int(os.environ.get("WEB_CONCURRENCY", str(max(1, multiprocessing.cpu_count() // 2 or 1))))
threads = int(os.environ.get("GUNICORN_THREADS", "8"))
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", "1000"))  # noop for gthread, kept for parity

# Automatically recycle workers to mitigate leaks
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "100"))

# Timeouts
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# -----------------------------
# Logging
# -----------------------------
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
accesslog = "-"   # stdout
errorlog  = "-"   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# -----------------------------
# Server mechanics (Render-friendly)
# -----------------------------
preload_app = True          # import app once in master, then fork
daemon = False              # must run in foreground on Render
pidfile = None
user = None
group = None
capture_output = True
forwarded_allow_ips = "*"   # trust Render proxy
worker_tmp_dir = "/dev/shm" if os.path.isdir("/dev/shm") else None

# Security / limits
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", "8190"))
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", "100"))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", "8190"))

proc_name = "xmrt-ecosystem"

# -----------------------------
# Lifecycle hooks
# -----------------------------
_bootstrapped = False

def when_ready(server):
    server.log.info("XMRT Ecosystem server is ready. Listening on %s", bind)

def post_fork(server, worker):
    """
    After each worker forks:
    - Initialize the main application and coordination core
    """
    global _bootstrapped
    try:
        from main import initialize_services
        if not _bootstrapped:
            initialize_services()  # Initialize the Flask app and coordinator
            _bootstrapped = True
            worker.log.info("✅ XMRT services initialized (worker pid=%s)", worker.pid)
        else:
            worker.log.info("↻ XMRT services already initialized (worker pid=%s)", worker.pid)
    except Exception as e:
        worker.log.exception("❌ Post-fork initialization error: %s", e)

def worker_int(worker):
    worker.log.info("Worker received INT/QUIT signal (pid=%s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal (pid=%s)", worker.pid)

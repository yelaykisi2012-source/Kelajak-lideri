import os

from app import app, init_db

secret_key = os.environ.get("KELAJAK_SECRET_KEY", "")
admin_password = os.environ.get("KELAJAK_ADMIN_PASSWORD", "")

if len(secret_key) < 32:
    raise RuntimeError("Set KELAJAK_SECRET_KEY to a random secret of at least 32 characters.")
if len(admin_password) < 12 or admin_password == "ChangeMe-2026!":
    raise RuntimeError("Set KELAJAK_ADMIN_PASSWORD to a unique password of at least 12 characters.")

init_db()

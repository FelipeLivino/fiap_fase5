from __future__ import annotations

from backend import create_app
from config import Settings


settings = Settings.from_env()
app = create_app(settings)


if __name__ == "__main__":
    app.run(
        host=settings.app_host,
        port=settings.app_port,
        debug=settings.app_debug,
    )

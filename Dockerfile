FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=10001:10001 app.py config.py ./
COPY --chown=10001:10001 backend ./backend
COPY --chown=10001:10001 tests ./tests
COPY --chown=10001:10001 watson ./watson

USER 10001:10001

EXPOSE 5000

CMD ["python", "app.py"]

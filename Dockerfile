FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c AS build
WORKDIR /build
COPY pyproject.toml requirements-runtime.lock.txt ./
COPY src ./src
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels -r requirements-runtime.lock.txt .

FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 \
    NAXJI_PERSISTENCE_MODE=postgres NAXJI_AUTH_MODE=supabase NAXJI_API_DOCS_ENABLED=false
WORKDIR /app
COPY --from=build /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels naxji-copilot-municipal-backend \
    && rm -rf /wheels \
    && useradd --system --uid 10001 --no-create-home naxji
COPY deploy/start.py /app/start.py
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/health',timeout=3)"
CMD ["python", "/app/start.py"]

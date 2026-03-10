FROM python:3.14.3-bookworm AS development
WORKDIR /home/appuser/app
COPY pyproject.toml .
COPY src/ src/
RUN pip install -e ".[dev]"

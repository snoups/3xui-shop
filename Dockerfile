FROM python:3.12-slim-bullseye

WORKDIR /app
ENV PYTHONPATH=/

COPY pyproject.toml /
RUN pip install poetry && poetry install

COPY ./app /app
COPY ./plans.json app/data/plans.json

RUN poetry run pybabel compile -d /app/locales -D bot
CMD ["poetry", "run", "python", "/app/__main__.py"]

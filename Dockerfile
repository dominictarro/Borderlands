FROM prefecthq/prefect:2-python3.11

COPY Pipfile Pipfile.lock .

RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv sync --system

FROM tiangolo/uvicorn-gunicorn-fastapi:latest
ENV PYTHONUNBUFFERED=true
WORKDIR /app

ENV POETRY_HOME=/opt/poetry
# ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# 生成新的 poetry.lock 文件
RUN poetry lock --no-update

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install coturn
RUN apt-get update && apt-get install -y coturn
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose the ports your turnserver is listening on
EXPOSE 3478 3478/udp
#Run coturn
CMD ["turnserver", "-c", "/etc/turnserver.conf"]

COPY . /app
ENV PYTHONPATH=/app

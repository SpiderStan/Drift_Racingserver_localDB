# Generic Poetry Build Stage
FROM python:3.9.7-slim as builder
RUN pip3 install "poetry==1.1.11"

# copy and build service to Wheel
WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY ./server ./server
RUN poetry build

# build the actual image with just Python + PIP
FROM tiangolo/uvicorn-gunicorn:python3.8-slim
COPY --from=builder /app/dist/server*.whl ./whl/
RUN pip3 install ./whl/*

RUN pip3 install dnspython
RUN pip3 install pymongo[srv]
RUN pip3 install backports.zoneinfo

# run service with uvicorn
EXPOSE 8001
ENTRYPOINT [ "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8001" ]

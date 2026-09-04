FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install llama-cpp-python
RUN pip install redis
CMD ["python", "-u", "main.py"]
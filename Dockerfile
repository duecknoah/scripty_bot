# Dockerfile for scripty-bot
FROM lucascosta/serverless-python3.6

ADD scripty-bot/ /

RUN pip install -U setuptools discord.py aioconsole

WORKDIR /src/
CMD ["python", "./scripty.py"]


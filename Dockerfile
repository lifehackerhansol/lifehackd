FROM python:3.11-bookworm

ENV HOME /home/lifehackd
RUN useradd -m lifehackd
WORKDIR $HOME
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt
USER lifehackd

COPY config.py config.py
COPY lifehackd.py lifehackd.py
COPY utils utils
COPY cogs cogs
COPY dbupdate dbupdate

RUN ln -sf /run/secrets/lifehackd-config config.json

CMD ["python3", "lifehackd.py"]

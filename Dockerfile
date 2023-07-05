FROM ubuntu:20.04

WORKDIR /app

COPY . .

RUN apt update -y

RUN apt install -y firefox
RUN export MOZ_HEADLESS=1

RUN apt install -y wget
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
RUN tar -xzf geckodriver-v0.33.0-linux64.tar.gz
RUN chmod +x geckodriver

RUN apt install -y gnome-keyring python3.8-venv python3-pip
RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt

CMD ["dbus-run-session", "--", "sh"]
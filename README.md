# PriceBot

<h3>This Repo is intended for Personal Use only.</h3>
It shows Product and their respective prices to the users.

# Deploy Methods
## Deploy to Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?button-url=https%3A%2F%2Fgithub.com%2Flanowde%2FPriceBot&template=https%3A%2F%2Fgithub.com%2Flanowde%2FPriceBot)

## Deploy Locally
```sh
git clone https://github.com/lanowde/PriceBot.git
nano .env
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel setuptools
pip install -r requirements.txt
python bot.py
```

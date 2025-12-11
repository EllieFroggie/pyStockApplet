# pyStockApplet - A simple helper to get and display stocks to waybar

A simple program to periodically grab data and host it on a local python webserver. The data is made available locally to dynamic endpoints to easily be grabbed by tools such as cURL. This allows stock prices to easily be added to displays such as waybar!

This program is very barebones, and probably not secure. I'll work on it when I have time, but i've already been procrastinating before my exams by making this. If (and i wouldn't reccomend it) you end up using this, DO NOT EXPOSE THE DOCKER CONTAINER TO THE OPEN INTERNET!

Realistically, this could have been done without the client server model. I personally, however, have more than one device making requests, and would probably get rate limited. The client-server model allows only one machine to make requests while multiple machines can access the data.


### Server: app.py

Requesting a ticker at `http://0.0.0.0:5000/v1/AAPL` will return the last market price queried for an asset.

The server is a simple python webserver running behind docker. It grabs data for the tickers specified in `config.json` and makes it available on a local network. This allows multiple devices to get data periodicaly while (hopefully) not getting rate limited by yahoo.

### Client: Whatever you use to make web requests

I use curl, since it's easy. `curl 0.0.0.0:5000/v1/AAPL`

### Ticker Selection

See `config.json`

## Installation and Setup:

### Clone and enter repo
`git clone https://github.com/EllieFroggie/pyStockApplet.git && cd pyStockApplet`

### Build and start the container

`docker build -t yquery-financials .`

`docker run -d -p 5000:5000 -v $(pwd)/config.json:/config/config.json --name yquery-financials yquery-financials:latest docker run -d -p 5000:5000 -v $(pwd)/config.json:/config/config.json --name yquery-financials yquery-financials:latest`

The webserver will now be running on port 5000.

pyStockApplet is now ready to go!

## Usage

To collect data on a ticker, add it to the "tickers" object in `config.json`, and restart the docker container. To try and prevent rate limiting, the server will not make api requests if american markets are closed. 

I originally built this project to display stock tickers in waybar. as such, the primary endpoint intended to be used is `http://0.0.0.0:5000/v1/<ticker>`, which returns the price of the chosen ticker in plaintext. 

Adding to waybar is as simple as:

```
"custom/pyStockTicker" :{
    "format": "<ticker>: {0}",
    "interval" : 330,
    "exec": "curl 0.0.0.0:5000/v1/AAPL" 
}
```
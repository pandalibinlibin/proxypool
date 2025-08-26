from flask import Flask, jsonify
from proxypool.db import RedisClient

app = Flask(__name__)
db = RedisClient()


class Server:
    def __init__(self):
        self.app = app

    def run(self, host="127.0.0.1", port=5000):
        """Start the Flask server.

        Args:
            host (str): The hostname to listen on. Defaults to '127.0.0.1'.
            port (int): The port of the webserver. Defaults to 5000.
        """
        self.app.run(host=host, port=port)


@app.route("/api/v1/random")
def get_random_proxy():
    """Get a random available proxy from Redis."""
    proxy = db.random()
    if proxy:
        return jsonify({"proxy": proxy})
    return jsonify({"message": "No proxy available"}), 404


@app.route("/api/v1/count")
def get_proxy_count():
    """Get the number of available proxies in Redis."""
    count = db.count()
    return jsonify({"count": count})


@app.route("/api/v1/all")
def get_all_proxies():
    """Get all proxies from Redis."""
    proxies = db.all()
    return jsonify({"proxies": list(proxies)})


if __name__ == "__main__":
    server = Server()
    server.run()

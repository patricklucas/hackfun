import json
import logging

import boto.dynamodb2
from boto.dynamodb2.table import Table
from flask import Flask, jsonify, render_template, request, abort
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer

REGION = "us-west-2"
KAFKA_BROKER = "10-40-31-139-uswest1cdevc"

COLORS = ["orange", "fuchsia", "green", "blue", "cyan"]

app = Flask(__name__)

dynamodb = boto.dynamodb2.connect_to_region(REGION)
the_table = Table("plucas_hack_1", connection=dynamodb)

kafka_client = KafkaClient([KAFKA_BROKER])
kafka_producer = SimpleProducer(kafka_client)


def get_records():
    queries = [{"key": color} for color in COLORS]
    records = the_table.batch_get(queries)
    return records


def make_message(key, value):
    return json.dumps({
        "key": key,
        "value": value,
    }).encode('utf-8')


def write_record(key, value):
    message = make_message(key, value)
    kafka_producer.send_messages("gds.writes", message)


@app.route("/")
def home():
    return render_template("home.html", region=REGION, colors=COLORS)


@app.route("/results")
def results():
    records = get_records()
    result = {r['key']: int(r.get('value')) for r in records}
    return jsonify(result)


@app.route("/update", methods=["POST"])
def update():
    key = request.form.get('key')
    value = request.form.get('value')

    if not key or not value:
        return abort(400)

    try:
        value = int(value)
    except ValueError:
        return abort(400)

    write_record(key, value)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=7938, debug=True)

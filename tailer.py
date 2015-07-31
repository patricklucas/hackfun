import json
import logging
import sys

import boto.dynamodb2
from boto.dynamodb2.table import Table
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

REGION = "us-west-2"
KAFKA_BROKER = "10-40-31-139-uswest1cdevc"


def main(region, broker):
    dynamodb = boto.dynamodb2.connect_to_region(region)
    the_table = Table("plucas_hack_1_master", connection=dynamodb)

    kafka_client = KafkaClient([broker])
    kafka_consumer = SimpleConsumer(kafka_client, "dynamodb-replication", "gds.writes")

    for offset_and_message in kafka_consumer:
        payload = offset_and_message.message.value
        payload_json = json.loads(payload.decode('utf-8'))
        key = {
            b'key': payload_json['key'].encode('utf-8'),
            b'value': payload_json['value'],
        }
        record = json.loads(offset_and_message.message.value.decode('utf-8'))
        print(record)
        the_table.put_item(record, overwrite=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    region, broker = sys.argv[1:]
    main(region, broker)

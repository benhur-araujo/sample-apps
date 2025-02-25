import os
import time
import sys
import pika
import threading

# RabbitMQ connection details (Bitnami defaults)
RABBITMQ_HOST ="rabbitmq-headless"
RABBITMQ_USER = "user"
RABBITMQ_PASSWORD = "MySupremePassword"
RABBITMQ_QUEUE = "test_queue"

def setup_rabbitmq_channel():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=credentials
    ))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return connection, channel

def producer():
    try: 
        connection, channel = setup_rabbitmq_channel()
        while True:
            message = f"Message sent at {time.time()}"
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent (write it to disk)
            )
            print(f" [x] Sent '{message}'", flush=True)
            time.sleep(1)
        
        connection.close()
    except Exception as e:
        print(f"Producer error: {e}", flush=True)
        time.sleep(2)

def consumer():
    def callback(ch, method, properties, body):
        message = body.decode()
        print(f" [x] Received {message}", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    while True:
        try:
            connection, channel = setup_rabbitmq_channel()
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
            print(" [*] Waiting for messages. To exit, press CTRL+C", flush=True)
            channel.start_consuming()
        except Exception as e:
            print(f"Consumer error: {e}", flush=True)
            time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "consumer":
        consumer()
    else:
        producer()

import time
import sys
from redis.sentinel import Sentinel, MasterNotFoundError

# Define Redis Sentinel connection
sentinel = Sentinel([('redis-headless', 26379)], socket_timeout=0.1)

# Ensure stdout is unbuffered for real-time logging
sys.stdout.reconfigure(line_buffering=True)

while True:
    try:
        while True:
            # Discover the master
            redis_master = sentinel.master_for('mymaster', socket_timeout=0.1)
            master_host, master_port = sentinel.discover_master('mymaster')
            
            # Print the current Master
            print(f'Current Redis Master: {master_host}:{master_port}', flush=True)
    
            # Increment the counter key
            redis_master.incr('counter')
            
            # Get current counter value & print it    
            counter_value = redis_master.get('counter')
            print(f'Counter: {counter_value.decode() if counter_value else "None"}', flush=True)
            time.sleep(1)
    
    except (MasterNotFoundError, ConnectionError, TimeoutError) as e:
        print(f"Lost connection to Redis Master. Retrying... Error: {e}", flush=True)
        time.sleep(2)  # Wait before retrying
    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        time.sleep(2)

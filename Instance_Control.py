import subprocess
import boto3
import time
import psutil
import redis

def stop_instance(instance_id, region):
    ec2_client = boto3.client('ec2', region_name=region)

    # Stop the instance
    ec2_client.stop_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is stopping...")

    # Wait for 10 minutes
    time.sleep(600)

def start_instance(instance_id, region):
    ec2_client = boto3.client('ec2', region_name=region)

    # Start the instance
    ec2_client.start_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is starting up...")

def monitor_cpu(threshold=90):
    # Monitor CPU usage
    while psutil.cpu_percent(interval=1) > threshold:
        print(f"CPU usage is above {threshold}%, waiting for it to decrease...")
        time.sleep(10)

def monitor_ram(threshold=90):
    # Monitor RAM usage
    while psutil.virtual_memory().percent > threshold:
        print(f"RAM usage is above {threshold}%, waiting for it to decrease...")
        time.sleep(10)

def increase_cpu():
    # You can implement logic here to increase CPU usage
    print("Increasing CPU usage...")

def increase_ram():
    # You can implement logic here to increase RAM usage
    print("Increasing RAM usage...")

def reset_cpu():
    # You can implement logic here to reset CPU usage to normal levels
    print("Resetting CPU usage to normal...")

def reset_ram():
    # You can implement logic here to reset RAM usage to normal levels
    print("Resetting RAM usage to normal...")

def connect_to_redis():
    # Replace the placeholders with your actual Redis server details
    redis_host = "your_redis_host"
    redis_port = 6379

    # Connect to Redis
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    print("Connected to Redis")

    # Use memtier_benchmark to write data to Redis
    subprocess.run(["memtier_benchmark", "--server", redis_host, "--port", str(redis_port), "--protocol", "redis", "--clients", "1", "--threads", "1", "--ratio", "1:0", "--key-pattern", "R:R", "--data-size-range", "1-100", "--data-size-pattern", "R", "--pipeline", "1", "--requests", "10000"])

def check_redis_stats():
    # Replace the placeholders with your actual Redis server details
    redis_host = "your_redis_host"
    redis_port = 6379

    # Connect to Redis
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Check CPU usage
    cpu_info = r.info('cpu')
    print(f"Redis CPU Usage: {cpu_info['used_cpu_sys']}")

    # Check memory usage
    memory_info = r.info('memory')
    print(f"Redis Memory Usage: {memory_info['used_memory_human']}")

if __name__ == "__main__":
    # Replace the placeholders with your actual values
    instance_id = "your_instance_id"
    region = "your_aws_region"

    # Prompt user for action
    user_choice = input("Choose an action:\n1. Stop Instance\n2. Increase CPU\n3. Increase RAM\n4. Connect to Redis and Write Data\n5. Check Redis Stats\nEnter the corresponding number: ")

    if user_choice == "1":
        # Stop the instance for 10 minutes
        stop_instance(instance_id, region)
        # Start the instance again
        start_instance(instance_id, region)
    elif user_choice == "2":
        # Monitor CPU usage and increase it
        monitor_cpu()
        increase_cpu()
        # Wait for a while to observe increased CPU usage
        time.sleep(300)
        # Reset CPU usage
        reset_cpu()
    elif user_choice == "3":
        # Monitor RAM usage and increase it
        monitor_ram()
        increase_ram()
        # Wait for a while to observe increased RAM usage
        time.sleep(300)
        # Reset RAM usage
        reset_ram()
    elif user_choice == "4":
        # Connect to Redis and write data
        connect_to_redis()
    elif user_choice == "5":
        # Check Redis stats
        check_redis_stats()
    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

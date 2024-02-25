import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def send_webhook_message(webhook_url, message):
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send webhook message. Status code: {response.status_code}")

def load_proxies_from_file(filename):
    with open(filename, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies

def check_group_status(group_id, webhook_url, proxies=None):
    url = f"https://groups.roblox.com/v1/groups/{group_id}"
    proxy = random.choice(proxies) if proxies else None
    response = requests.get(url, proxies={"http": proxy, "https": proxy})
    
    if response.status_code == 200:
        group_data = response.json()
        if 'owner' in group_data:
            if group_data['owner']:
                print(f"Group {group_id} is owned by {group_data['owner']['username']}.")
                return  # Skip sending webhook message
        else:
            print(f"Unable to determine status for group {group_id}.")
            return  # Skip sending webhook message

        if 'isLocked' in group_data:
            if group_data['isLocked']:
                send_webhook_message(webhook_url, f"Group {group_id} is locked.")
            else:
                send_webhook_message(webhook_url, f"Group {group_id} is not locked.")
        else:
            print(f"Unable to determine lock status for group {group_id}.")
    else:
        print(f"Failed to fetch group data for {group_id}. Error {response.status_code}.")

if __name__ == "__main__":
    start_id = 32876500
    end_id = 34700000
    webhook_url = input("Enter the webhook URL: ")
    proxy_file = "proxies.txt"
    threads = int(input("Enter the number of threads: "))
    cores = int(input("Enter the number of cores: "))

    proxies = load_proxies_from_file(proxy_file)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for group_id in range(start_id, end_id + 1):
            future = executor.submit(check_group_status, group_id, webhook_url, proxies)
            futures.append(future)
        
        for future in as_completed(futures):
            future.result()

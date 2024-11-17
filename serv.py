import requests
import time

TIME = 30  # Interval between requests
starttime = time.time()

while True:
    try:
        response = requests.get('https://jj-wzj6.onrender.com/status')  # Use localhost or a valid address
        print(f"Status Code: {response.status_code}, Time: {time.ctime()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
    # Ensure the sleep interval is consistent
    time.sleep(TIME - ((time.time() - starttime) % TIME))

from locust import HttpUser, task, events
from locust.exception import StopUser
import sys

class CacheRaceCondition(HttpUser):
    
    @task
    def simulate(self):
        response = self.client.get(f"/cache/?key=test-1")
        if response.status_code == 409:
            print(response.text)
            print("Reached target status code")
            sys.exit(1)
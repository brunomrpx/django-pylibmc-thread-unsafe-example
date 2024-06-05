.PHONY: test
test:
	@ docker run --rm \
		-v $(PWD):/mnt/locust \
		--network=sample-network \
		-w /mnt/locust \
		locustio/locust:latest --headless --users 100 --spawn-rate 1 --run-time 1m -H http://sample-app:8000

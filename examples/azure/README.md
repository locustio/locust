This folder contains examples of how to run Locust tests using Azure Load Testing.

It shows off a moderately complex scenario where the Locust file depends on additional files as well as external packages specified in requirements.txt.

az load test create --load-test-resource my-load-test-resource --resource-group my-test-resource-group --test-id my-test-id --load-test-config-file loadtest.config.yaml

az load test-run create --load-test-resource my-load-test-resource --resource-group my-test-resource-group --test-id my-test-id

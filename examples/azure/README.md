This folder contains examples of how to run Locust tests with dependencies in a requirements.txt file, suitable for use in Azure Load Testing.

[postgres](postgres.yaml) example only relies on external dependencies, [grpc](grpc.yaml) shows a more complex scenario where we also use multiple Python files.

az load test create --load-test-resource my-load-test-resource --resource-group my-test-resource-group --test-id my-test-id --load-test-config-file grpc.yaml

az load test-run create --load-test-resource my-load-test-resource --resource-group my-test-resource-group --test-id my-test-id

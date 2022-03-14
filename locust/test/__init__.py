try:
    import resource

    # work around occasional "zmq.error.ZMQError: Too many open files"
    # this is done in main.py when running locust proper so we need to do it here as well
    resource.setrlimit(
        resource.RLIMIT_NOFILE,
        (
            10000,
            resource.RLIM_INFINITY,
        ),
    )
    changed_rlimit = True
except Exception:
    changed_rlimit = False

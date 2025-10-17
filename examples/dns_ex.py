from locust import run_single_user, task
from locust.contrib.dns import DNSUser

import time

import dns.message
import dns.rdatatype


class MyDNSUser(DNSUser):
    @task
    def t(self):
        message = dns.message.make_query("example.com", dns.rdatatype.A)
        # self.client wraps all dns.query methods https://dnspython.readthedocs.io/en/stable/query.html
        self.client.udp(message, "8.8.8.8")
        self.client.tcp(message, "1.1.1.1")
        self.client.udp(
            dns.message.make_query("doesnot-exist-1234234.com", dns.rdatatype.A),
            "1.1.1.1",
            name="You can rename requests",
        )
        # don't spam other people's DNS servers
        time.sleep(10)


if __name__ == "__main__":
    run_single_user(MyDNSUser)

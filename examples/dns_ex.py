from locust import run_single_user, task
from locust.contrib.dns import DNSUser

import dns.message
import dns.rdatatype


class MyDNSUser(DNSUser):
    @task
    def t(self):
        message = dns.message.make_query("example.com", dns.rdatatype.A)
        self.client.udp(message, "8.8.8.8")
        self.client.udp(message, "4.4.4.4", name="Use other dns server")


if __name__ == "__main__":
    run_single_user(MyDNSUser)

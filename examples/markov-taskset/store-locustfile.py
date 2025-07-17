from locust import constant, HttpUser
from locust.user.markov_taskset import MarkovTaskSet, transition, transitions


class ShoppingBehavior(MarkovTaskSet):
    wait_time = constant(1)

    @transition("view_product")
    def browse_catalog(self):
        self.client.get("/catalog")

    @transitions({
        "add_to_cart": 3,  # Higher probability
        "browse_catalog": 1,
        "checkout": 1
    })
    def view_product(self):
        self.client.get("/product/1")

    @transitions(["view_product", "checkout"])
    def add_to_cart(self):
        self.client.post("/cart/add", json={"product_id": 1})

    @transition("browse_catalog")
    def checkout(self):
        self.client.post("/checkout")
        self.interrupt(reschedule=False)


class ShopperUser(HttpUser):
    host = "http://127.0.0.1"
    tasks = {ShoppingBehavior: 1}

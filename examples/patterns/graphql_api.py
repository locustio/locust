"""
GraphQL API Load Testing

This example demonstrates how to test GraphQL APIs with queries and mutations.

Usage:
    locust -f graphql_api.py --host=http://localhost:8000
"""

from locust import HttpUser, between, task


class GraphQLUser(HttpUser):
    """Simulates users querying GraphQL API"""

    wait_time = between(1, 3)

    @task(2)
    def query_items(self):
        """Execute a GraphQL query to list items"""
        query = """
        query {
            items {
                id
                name
                price
            }
        }
        """

        self.client.post(
            "/graphql",
            json={"query": query},
            name="query_items"
        )

    @task(1)
    def query_item_by_id(self):
        """Query a specific item"""
        query = """
        query {
            item(id: 42) {
                id
                name
                price
                description
            }
        }
        """

        self.client.post(
            "/graphql",
            json={"query": query},
            name="query_item_by_id"
        )

    @task(1)
    def mutation_create_item(self):
        """Create an item using mutation"""
        mutation = """
        mutation {
            createItem(input: {
                name: "New Item"
                price: 99.99
                description: "Test item"
            }) {
                id
                name
                price
            }
        }
        """

        self.client.post(
            "/graphql",
            json={"query": mutation},
            name="mutation_create_item"
        )

    @task(1)
    def query_with_variables(self):
        """Query with variables"""
        query = """
        query GetItem($id: ID!) {
            item(id: $id) {
                id
                name
                price
            }
        }
        """

        self.client.post(
            "/graphql",
            json={
                "query": query,
                "variables": {"id": "42"}
            },
            name="query_with_variables"
        )

    @task(1)
    def mutation_with_variables(self):
        """Mutation with variables"""
        mutation = """
        mutation UpdateItem($id: ID!, $name: String!) {
            updateItem(id: $id, input: {name: $name}) {
                id
                name
            }
        }
        """

        self.client.post(
            "/graphql",
            json={
                "query": mutation,
                "variables": {
                    "id": "42",
                    "name": "Updated Name"
                }
            },
            name="mutation_with_variables"
        )


if __name__ == "__main__":
    print("GraphQL API Load Testing Example")
    print("Usage: locust -f graphql_api.py --host=http://localhost:8000")

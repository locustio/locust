import locust
from locust.user import task
from archivist.archivist import Archivist  # Example SDK under test


class ArchivistUser(locust.HttpUser):
    def on_start(self):
        AUTH_TOKEN = None

        with open("auth.text") as f:
            AUTH_TOKEN = f.read()

        # Start an instance of of the SDK
        self.arch: Archivist = Archivist(url=self.host, auth=AUTH_TOKEN)
        # overwrite the internal _session attribute with the locust session
        self.arch._session = self.client

    @task
    def Create_assets(self):
        """User creates assets as fast as possible"""

        while True:
            self.arch.assets.create(behaviours=["Builtin", "RecordEvidence", "Attachments"], attrs={"foo": "bar"})

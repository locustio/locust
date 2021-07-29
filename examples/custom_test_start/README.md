# Custom Start UI

This Example shows how to use flasks Blueprints and templates to add custom items to the start of a loadtest.

## Files:
- `extend_test_start.py:` This file contains a sample locustfile with the necessary routes to get the data from the forms
and share them to the requests. 
- `templates/extend_test_start.html: ` This file contains the extended html blocks that utilises flasks templates to
integrate new html code to locusts UI
- `static/extended_test_start.js:` This file has ajax code that posts the new forms to the backend to send the new authentication
data to the request objects
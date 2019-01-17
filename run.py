#!flask/bin/python
from mp import app
import config

app.run(debug=config.debug)
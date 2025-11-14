"""Start server with explicit error logging.
"""
from agrifarma import create_app
from config import DevelopmentConfig
import logging

logging.basicConfig(level=logging.DEBUG)

app = create_app(DevelopmentConfig)
app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

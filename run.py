from app import create_app
import os

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        ssl_context="adhoc"
    )

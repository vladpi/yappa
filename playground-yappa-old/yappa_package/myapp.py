from yappa.flask_yandex import FlaskYandex

app = FlaskYandex(__name__)


@app.route('/')
def main():
    return 'Hello from Yappa!'
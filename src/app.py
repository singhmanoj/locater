from locater import create_app, create_celery_app

app = create_app()
from locater import celery

if __name__ == '__main__':
    app.run(debug=True)
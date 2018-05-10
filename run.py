from app import app
from app.home import main as main_blueprint

app.register_blueprint(main_blueprint, )
if __name__ == '__main__':
    app.run()
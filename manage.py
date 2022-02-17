import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from application import blueprint
# from application import app, db
from application.main import create_app, db
from flask_cors import CORS
# from logging import FileHandler, DEBUG
import logging

app = create_app(os.getenv('DISWIKI_SERVER_ENV') or 'prod')
app.register_blueprint(blueprint)

app.app_context().push()

CORS(app, resources={r'/*': {'origins': '*'}})

app.app_context().push()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# ERROR LOG
# if not app.debug:
#   file_hameler = FileHandler('error_logs.txt')
#   file_hameler.setLevel(DEBUG)
#   app.logger.addHandler(file_hameler)
logging.basicConfig(filename='error.log', level=logging.DEBUG)


@app.after_request
def after_request(response):
    db.session.close()
    return response


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def delete_db():
    """Creates the db tables."""
    db.drop_all()


@manager.command
def run():
    app.run()
    # app.run(port=8181, host='0.0.0.0', debug=True)


@manager.command
def test():
    ""
    # tests = unittest.TestLoader().discover('test', pattern='test*.py')
    # result = unittest.TextTestRunner(verbosity=2).run(tests)
    # if result.wasSuccessful():
    #     return 0
    # return 1


# @manager.command
# def test():
#     """Runs the unit tests."""
#     tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         return 0
#     return 1
if __name__ == '__main__':
    manager.run()

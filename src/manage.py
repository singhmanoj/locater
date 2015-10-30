from flask.ext.script import Manager
import sys

from locater import create_app

# env Locater_CONFIG_NAME=Testing python manage.py test

manager = Manager(create_app)

@manager.command
def hello():
    print "hello"

if __name__ == "__main__":
    if sys.argv[1] == 'test':
        # import os    #this is to be done after all
        # os.environ['rocket_CONFIG_NAME']='Testing'
        manager = Manager(create_app(package_name='locater'))
        @manager.command
        def test():
            import nose
            nose.main(argv=['locater.test', '-s', '-v', '--with-coverage', '--cover-package', 'locater'])
        manager.run()
    else:
        manager.run()
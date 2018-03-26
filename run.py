import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Run Weight Server.')
parser.add_argument('-username', '-u',
                    required=True,
                    type=str,
                    nargs=1,
                    dest='username',
                    help='Username for Postgres Database')
parser.add_argument('-password', '-p',
                    required=True,
                    type=str,
                    nargs=1,
                    dest='password',
                    help='Password for Postgres Database User')
parser.add_argument('-database', '-d', '-db',
                    required=True,
                    type=str,
                    nargs=1,
                    dest='database',
                    help='Postgres Database to Connect To')



args = parser.parse_args()
os.environ['FLASK_DEBUG'] = '1'
os.environ['FLASK_APP'] = 'Weight.py'
os.environ['DATABASE_URL'] = 'postgresql://{}:{}@localhost:5432/{}'.format(args.username[0], args.password[0], args.database[0])
os.environ['SECRET_KEY_PRACTICE_PRACTICE'] = 'WJFEJEWFEWFJPEFeWEFOWFEEWMFEFOWFE'
subprocess.run('flask run', stdout=subprocess.PIPE, shell=True)
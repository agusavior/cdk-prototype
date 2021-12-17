import logging
import sys
import subprocess

def run(command, cwd=None):
    subprocess.run(command.split(), cwd=cwd)

# ==========
# BUILD APPS
# ==========

logging.info('Building...')

# Build Elastic Beanstalk Application
run('zip --version')
run('mkdir build')

# Make app.zip
run('zip -r app.zip .', cwd='./../eb-application')
# TODO: Use a different name on the app.zip because the name of the zip has to cotain some unique value, like
# the version of the app. Read more about it on: https://stackoverflow.com/questions/51155927/during-an-aborted-deployment-some-instances-may-have-deployed-the-new-applicati/51833138
run('mv ./../eb-application/app.zip ./build/')

logging.info('Done.\n Now you may run `cdk deploy`.')
sys.exit(0)

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
run('mv ./../eb-application/app.zip ./build/')

logging.info('Done.\n Now you can run `cdk deploy` if you want.')
sys.exit(0)

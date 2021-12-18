# Example processing app


## Getting started

Let's suppose you want to run the proyect. You will need to install python and depedencies of the proyect. It's recommended to use some virtual environment for python packages. In this case, we'll use venv.

These commands have been tested on Ubuntu 20.04.

```bash
# Install python 3.
# At the moment this was written, this commands install python 3.8.10
sudo apt-get update
sudo apt-get install python3

# Install venv
sudo apt-get install python3-dev python3-venv

# Clone the proyect and then...
# TODO: Edit the name of the subproject.
cd processing/playing-with-amqp

# Create the .venv directory.
# This assume that your python 3 binary is located in /usr/bin/python3
/usr/bin/python3 -m venv .venv/

# Activate the python venv environment
source ./.venv/bin/activate

# Now you should see a '(.venv)' in your terminal
# Just in case, upgrade pip
pip install --upgrade pip

# Install the proyect python packages
pip install -r requirements.txt

# Create env.py
cp env_example.py env.py

# Fill the fields inside the file just copied
nano env.py

# Run it
python __init__.py

```

## Build and run the image locally

```bash
# Create env.py
cp env_example.py env.py

# Fill the fields inside the file just copied
nano env.py

# Build the image
docker build -t image0 .

# Run it
docker run image0
```

## Push the image to Docker Hub

```bash
# Build the image
docker build -t image0 .

# If you want to build it for amd64
docker build -t image0 . --platform linux/amd64

# Run it
docker run image0

# Tag it
docker image tag image0 repo/app-name:latest

# Push it
docker image push repo/app-name:latest
```

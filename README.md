# Welcome to CDK Prototype

## Getting started

First, you need to install AWS CLI. Then, use this command to set up the credentials of you AWS account.
```bash
aws configure
```

Install AWS CDK
```bash
sudo npm install -g aws-cdk
```

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```bash
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```bash
.venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```bash
cdk synth
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

## About your domain

Do not forget to set up the namespaces correctly once the AWS Zone Name is created.
Go to your route53, open the zone, and copy the four namespaces.Then, go to your domain provider and paste the namespaces in the configuration of the domain.

<TO-DO> Move the above comment to another place.

## Miscellaneous

If you don't want to install AWS CDK globally, you can using it with "npx" like so
```bash
npx aws-cdk <subcommand>
```

In order to create this project, AWS CDK version 2.1.0 has been used.

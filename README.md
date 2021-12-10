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

## Useful commands of CDK

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Troubleshooting

### Can't deploy because certificate isn't created

This could be because you have to configure the namespaces of your domain.
Follow the next steps:
1. Run `cdk deploy`.
2. Wait until your CDK creates the Hosted Zone.
3. Log in in AWS Console and go to your hosted zones.
4. Go to the hosted zone that CDK created.
5. You'll see four namespaces in the column `Value/Route traffic to`.
6. Copy each one and go to your domain provider, (for instance domain.com).
7. Select your domain y go to its configuration.
8. Find some "namespaces" list.
9. Paste the copied namespaces that you copied in the step 5.
10. Save it.
11. Wait until the command `cdk deploy` finishes.

### Can't delete the stack with cdk destroy

Maybe this is because you have to delete your Hosted Zone manually. 
This seems to be an issue: https://github.com/aws/aws-cdk/issues/4155
## Miscellaneous

If you don't want to install AWS CDK globally, you can using it with "npx" like so
```bash
npx aws-cdk <subcommand>
```

In order to create this project, AWS CDK version 2.1.0 has been used.

If you deploy this, you'll see an AWS Cloudformation Stack called CDKToolkit listed. Don't worry about it, CDK created that for its purpose.

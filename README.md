# PingPongBracketsLambda

## Create Bracket: src/create-bracket

In this directory we have another template.yaml file as well as a create_bracket subdirectory. We wanted to make each of the lambda functions available for a stand-alone deployment, thusly the template.yaml is a SAM template just for this function. Looking inside the create_bracket subdirectory we find requirements.txt, __init__.py and create_bracket.py. If you are familiar with Python you will undoubtedly know what these are already. For those that are new, the requirements.txt is basically a list of dependencies for your lambda function (similar to a Gemfile or package.json). __init__.py used to be for marking a directory on disk as a Python package prior to Python3.3 when implicit namespace packages were introduced. The algorithm in the create_rounds method is a little complex:

The goal of the algorithm is to take an array of users plus a bracket ID and create a matrix of games played out over an even number of rounds to determine a champion. The algorithm must match 2 sets of opponents by their seeding going into the tournament, i.e. #1 plays #4 and #2 plays #3.

## Create Result: src/create-result

Once a game has been played and a final score has been determined we need a way to update DynamoDB, both the games and the brackets table, with this new info for the game and determine the next round in the tournament. To interact with DynamoDB we use the standard SDK for AWS on Python called Boto3.

## List Users: src/get-cognito-users

This is a simple Node.js Lambda function that gives us a list of the users in our platform. The users are stored in a User Pool which is part of the AWS Cognito service.

## Adding a new Serverless Function

If you want to add a new function in addition to the ones in the sample repo, the CLI command is pretty simple:

    $ sam init --runtime nodejs14.x -n <function name>


## The Deploy Script: deployLambdas.sh

Now that we understand the structure of the serverless backend lets deploy it to the cloud. To begin, start your Docker Desktop app:
Docker

Next, run the deploy script (if you are working on a Windows OS run this using the Git Bash app). This will build the lambda functions in a Linux environment on a Docker container, making them compatible with the cloud Linux environment where they will ultimately reside:

    $ ./deployLambdas.sh <YOUR AWS PROFILE NAME> <S3 BUCKET NAME> <STACK NAME>

This script will take the lambda code, do a compile/build/whatever, and deploy it to the S3 bucket we created. This will make the function available in the AWS Lambda service and we can run our functions in response to an API request now.

## Conclusion

After deploying all the backend resources you should be in a stable spot to run the web app part of the platform. By no means is this “production-ready” code. In the real world you will want to add unit testing, integration testing, stricter IAM permissions, etc. to the final product.

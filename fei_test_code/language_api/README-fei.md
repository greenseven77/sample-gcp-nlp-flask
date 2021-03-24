# Python Google Natural Language Cloud  sample for Google App Engine Flexible Environment


## Setup

Project name: gee-m2-project

Create your App Engine application: 
    gcloud app create

Set an environment variable for your project ID:

    export PROJECT_ID=$(gcloud config get-value core/project)

## Getting the sample code

Run the following command to clone the Github repository:

    git clone https://github.com/Jiaxen/sample-gcp-nlp-flask.git

Change directory to the sample code location:

    cd sample-gcp-nlp-flask/language_api

## Authentication

Enable the APIs: (You can also do these through Navigation Menu -> APIs & Services)

    gcloud services enable language.googleapis.com
    gcloud services enable datastore.googleapis.com

Create a Service Account to access the Google Cloud APIs when testing locally:

    gcloud iam service-accounts create example \
    --display-name "My Service Account"

Give your newly created Service Account appropriate permissions:

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:example@${PROJECT_ID}.iam.gserviceaccount.com \
    --role roles/owner

After creating your Service Account, create a Service Account key:

    gcloud iam service-accounts keys create ~/key.json --iam-account \
    example@${PROJECT_ID}.iam.gserviceaccount.com

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to where
you just put your Service Account key:

    export GOOGLE_APPLICATION_CREDENTIALS="/home/${USER}/key.json"

## Running locally

Create a virtual environment and install dependencies:

    virtualenv -p python3 env
    source env/bin/activate
    pip install -r requirements.txt

Note that if you have to restart (re-activate) your virtual environment, keep in mind to do it from this directory where you have created the env, or it wont work.

Start your application locally:

    python main.py

Visit the link generated ('Running on http://127.0.0.1:8080/') to view your application running locally. Press `Control-C`
on your command line when you are finished.

When you are ready to leave your virtual environment:

    deactivate
    
## Running tests

To run tests, install the requirements for your test
    
    pip install -r requirements-test.txt

Then run pytest by doing  
    
    python -m pytest

## Deploying to App Engine

Deploy your application to App Engine with the following command. Please note that this may
take several minutes.

    gcloud app deploy

PUBLIC URL: https://gee-m2-project.appspot.com/

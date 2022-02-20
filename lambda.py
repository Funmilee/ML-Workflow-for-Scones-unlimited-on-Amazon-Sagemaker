#serialize
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = "sagemaker-us-east-1-889610354338"
    # Download the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key, '/tmp/image.png')
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

#classify

import json
import base64
import boto3
# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2021-12-26-17-14-32-102"
def lambda_handler(event, context):
   # Decode the image data
    body = event["body"]
    image = base64.b64decode(event["body"]["image_data"]) ## TODO: fill in
    # Instantiate a Predictor
    runtime = boto3.client('runtime.sagemaker')
    
    # Make a prediction:
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType="image/png",Body=image)
    inferences = json.loads(response['Body'].read().decode('utf-8'))
    print("...inferences:", inferences)
    # We return the data back to the Step Function    
    return {
        'statusCode': 200,
        'body': {
            "inferences": inferences
        }
    }

#

import json
THRESHOLD = .99
def lambda_handler(event, context):
    inferences = event["body"]["inferences"]
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = inferences[0] > THRESHOLD or inferences[1] > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
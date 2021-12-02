"""Uploader class & helper methods."""

import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()  # take environment variables from .env.
UPLOAD_FOLDER = os.getenv('S3_LOCATION')
BUCKET_NAME = os.getenv('S3_BUCKET')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

class Uploader:
    """Create user paths, upload & display user images, and delete user images from Amazon S3 bucket."""

    def __init__(self, user_id):
        self.user_id = user_id

    def create_bucket(self):
        """Create a new uploads path object in S3 for this user."""

        s3 = ''
        try:
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            #create new path & set
            new_directory_name = f'uploads/user/{self.user_id}/'
            s3.put_object(Bucket=BUCKET_NAME, Key=(new_directory_name))

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                print("Invalid credentials.")
            else:
                print(f'Unexpected error: {e}')
                

    def upload_image(self, key, img):
        """Upload a user's image to their upload path and return the url of the uploaded image."""
        try:
            s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            # upload the image in the specified folder(key)
            s3.Bucket(BUCKET_NAME).put_object(Key=key+img.filename, Body=img)

            return f'{UPLOAD_FOLDER}{self.user_id}/{img.filename}'

        except ClientError as e:
            print(f'Error uploading image: {e}')
            return None

    def delete_image(self, url):
        """Delete a user's image from the user upload path using the file name."""
        try:
            s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = s3.Bucket(BUCKET_NAME)
            file_name = os.path.basename(url);
            for obj in bucket.objects.filter(Prefix=f'uploads/user/{self.user_id}/'):
                if (file_name in obj.key):
                    obj.delete()

        except ClientError as e:
            print(f'Error deleting the image: {e}')

    def delete_all(self):
        """Delete all of a user's images and upload path from S3."""
        try:
            s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = s3.Bucket(BUCKET_NAME)
            for obj in bucket.objects.filter(Prefix=f'uploads/user/{self.user_id}/'):
                obj.delete()

        except ClientError as e:
            print(f'Error deleting user images/directory: {e}')

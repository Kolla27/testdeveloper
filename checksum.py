#! /usr/bin/python
import os 
import hashlib
from os import listdir
from os.path import isfile, join
import boto3
import botocore


#accessKeyId     = os.environ['accessKeyId']
#secretAccessKey = os.environ['secretAccessKey']
bucketname      = os.environ['bucketname']
tlsValue        = True

newVar = os.getcwd()
mypath = newVar + '/' #change it to the Jenkins job path

#mypath = '/home/ec2-user/python_code'
fileList = [f for f in listdir(mypath) if isfile(join(mypath, f))]

unmatch_list = []
notCopied_list = []

hash_mapper_local = {}
hash_mapper_s3 = {}

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

for item in fileList:
    hash_value = md5(item)
    hash_mapper_local[item] = hash_value

#print hash_mapper_local

s3 = boto3.resource('s3')
def s3_md5sum(bucket_name, resource_name):
    try:
        md5sum = boto3.client('s3').head_object(
            Bucket=bucket_name,
            Key=resource_name
        )['ETag'][1:-1]
    except botocore.exceptions.ClientError:
        md5sum = None
        pass
    return md5sum

def dif_checksum(d1, d2):
    for k1, v1 in d1.items():
        if d2.has_key(k1):
            if d2[k1] == v1:
                pass
            else:
                if d2[k1] == None:
                    notCopied_list.append(k1)
                else:
                    unmatch_list.append(k1)
        else:
            notCopied_list.append(k1)
    if len(unmatch_list) > 0:
        print "Below are the files whose checksum is different. These may be corrupted and requires upload again."
        for i in unmatch_list:
            print i
    if len(notCopied_list) > 0:
        print "Below are the files which are not uploaded to S3."
        for i in notCopied_list:
            print i   

for item1 in fileList:
    new_hash_value = s3_md5sum(bucketname, item1)
    hash_mapper_s3[item1] = new_hash_value


#print hash_mapper_s3

#s3_md5sum('jenkinstestkolla', '159863_356_9222_1-SIGN.png')

dif_checksum(hash_mapper_local, hash_mapper_s3)
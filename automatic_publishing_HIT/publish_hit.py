import boto3

region_name = 'us-east-1'
aws_access_key_id = 'XXXXX'
aws_secret_access_key = 'XXXXX'

endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# This will return $10,000.00 in the MTurk Developer Sandbox
# print(client.get_account_balance()['AvailableBalance'])

question = open(file='test_questions.xml', mode='r').read()

new_hit = client.create_hit_with_hit_type(
    HITTypeId='3M7B7ZP99W63UJW5XGU8EYGZAGLIR1',
    HITLayoutId='3XWHG9Y36J7YA1LPKFP3PQEPCNU2RT',
    LifetimeInSeconds=60 * 60 * 24 * 7
)

print("A new HIT has been created. You can preview it here:")
print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
# Remember to modify the URL above when you're publishing
# HITs to the live marketplace.
# Use: https://worker.mturk.com/mturk/preview?groupId=

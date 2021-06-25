#
# Ed Silva
#
# Version 1.0
# June 21, 2021
#
# Use at your own risk and is provided As-Is without any kind of warranties. 
#
# This script prints out all target groups the
# provided EC2 belongs to. The scripts takes a single
# or many EC2s. It will first verify that the EC2s exists
# and if not it will be removed from the provided list
# before the search starts.
#
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
#
# aws elbv2 describe-target-groups --query 'TargetGroups[*].TargetGroupArn[]' --output json
# aws elbv2 describe-target-health  --target-group-arn
#
import boto3
import botocore
import getopt
import sys

#
# Assing non-duplicate EC2s Id
#
argv  = list(set(sys.argv[1:]))
my_ec2_ids = sys.argv[1:]

if (len(my_ec2_ids) < 1 ):

        print("Usage: {} <EC2 InstanceId> ... <EC2 InstanceId>".format(sys.argv[0]))
        exit(1)

client_elbv2 = boto3.client('elbv2')
client_ec2 = boto3.client('ec2')
r_describe_target_groups = client_elbv2.describe_target_groups()
my_tg = len(r_describe_target_groups['TargetGroups'])

if( my_tg == 0 ):
        print(" ")
        print("  No Target Groups deployed")
        print(" ")
        exit(1)

y = 0
for x in range(len(argv)):
	try:
		r_describe_instances = client_ec2.describe_instances(InstanceIds=[argv[x]])
	except botocore.exceptions.ClientError:
		my_ec2_ids.remove(argv[x])
		print("Removed invalid EC2 Id: {}".format(argv[x]))
	y+=1
	
if (len(my_ec2_ids) ==  0):
        print("Not valid EC2 Id found!")
        exit(1)

for i in range(my_tg):

	tg_name = format(r_describe_target_groups['TargetGroups'][i]['TargetGroupName'])
	tg_arn = format(r_describe_target_groups['TargetGroups'][i]['TargetGroupArn'])
	r_describe_target_health = client_elbv2.describe_target_health(**{"TargetGroupArn": tg_arn})
	my_tg_lb_arn = len(format(r_describe_target_groups['TargetGroups'][i]['LoadBalancerArns']))

	if ( my_tg_lb_arn > 2 ):

		tg_lb_arn = format(r_describe_target_groups['TargetGroups'][i]['LoadBalancerArns'][0])
		r_describe_load_balancers = client_elbv2.describe_load_balancers(**{"LoadBalancerArns": r_describe_target_groups['TargetGroups'][i]['LoadBalancerArns'] })
		tb_lb = r_describe_load_balancers['LoadBalancers'][0]['LoadBalancerName']

	my_th = len( r_describe_target_health['TargetHealthDescriptions'] )

	if ( my_th != 0 ):
		for x in range(my_th):
			for y in range(len(my_ec2_ids)):
				r_describe_instances = client_ec2.describe_instances(InstanceIds=[my_ec2_ids[y]])
				if ( my_ec2_ids[y] == r_describe_target_health['TargetHealthDescriptions'][x]['Target']['Id']):
					print ("{}: {}".format(tg_name, my_ec2_ids[y]))


exit(0)

#-- coding:utf-8 --

class Client_S3:

    def __init__(self, iamProfilename):
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.s3 = self.session.client('s3')

    def _getBucketList(self):
        # Reference : http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_buckets
        response = self.s3.list_buckets()
        return(response)
    
    def _removeSpecificBucket(self, bucketName):
        # Reference : http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.delete_bucket
        response = self.s3.delete_bucket(
            Bucket= bucketName
        )
        return(response)

class Resource_Dynamodb :

    def __init__(self,iamProfilename,tableName) :
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.dynamodb = self.session.resource('dynamodb')
        self.table = self.dynamodb.Table(tableName)

    def _getCountOfQueryResult(self, partitionKey, condiTion):
        from boto3.dynamodb.conditions import Key
        # Reference1 : https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.04.html
        # Reference2 : http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.query
        response = self.table.query(
            KeyConditionExpression = Key(partitionKey).eq(condiTion),
            Select = 'COUNT'
        )
        return(response)

class Client_Dynamodb:

    def __init__(self, iamProfilename):
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.dynamodb = self.session.client('dynamodb')

    def _getTableDescription(self, tableName):
        # Reference1 : http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.describe_table
        response = self.dynamodb.describe_table(
            TableName = tableName
        )
        return(response)

class Resource_Ec2 :

    def __init__(self,iamProfilename) :
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.ec2 = self.session.resource('ec2')        

    #Get EC2 instance list
    def _getEntireListofCurrentInstances(self) :
        response = [{'instance.id':instance.id,'instance.state':instance.state} for instance in self.ec2.instances.all()]
        return(response)

    #Create and Run EC2 instance
    def _createNewInstances(self,imageId,minCount,maxCount,instanceType,keyName,securityGroupIds,iamInstanceProfile,instanceTags,userData) :
        instance = self.ec2.create_instances(
                            #create_instances Arguments References : http://docs.aws.amazon.com/ko_kr/cli/latest/userguide/generate-cli-skeleton.html
            ImageId = imageId, 
            MinCount = minCount,
            MaxCount = maxCount,
            InstanceType = instanceType,
            KeyName = keyName,
            SecurityGroupIds = securityGroupIds,
            IamInstanceProfile = iamInstanceProfile,
            TagSpecifications = [
                    {
                        'ResourceType': 'instance',
                        #ResourceType SHOULD BE in TagSpecifications
                        'Tags': [
                            instanceTags,
                        ]
                    }
                ],
            UserData = userData,
            )
        return(instance)

    #Stop EC2 instances
    def _stopInstances(self,instanceIds) :
        instance = self.ec2.instances.filter(InstanceIds=instanceIds)
        response = instance.stop()
        return(response)

    #Start EC2 instances
    def _startInstances(self,instanceIds) :
        instance = self.ec2.instances.filter(InstanceIds=instanceIds)
        #Case#01 instance type is not supported on specific AWS region(e.g. ap-northeast-2) : botocore.exceptions.ClientError: An error occurred (Unsupported) when calling the StartInstances operation: The requested configuration is currently not supported. Please check the documentation for supported configurations.
        #Case#01 Trouble Shooting : chek the limits and change the instance type available, https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/ec2-resource-limits.html
        #Case#01 Ref : m5.large is not supported on ap-northeaset-2, https://aws.amazon.com/ko/blogs/korea/m5-the-next-generation-of-general-purpose-ec2-instances
        response = instance.start()
        return(response)

    #Terminate EC2 instances
    def _terminateInstances(self,instanceIds) :
        instance = self.ec2.instances.filter(InstanceIds=instanceIds)
        response = instance.terminate()
        return(response)

class Client_Ec2 :

    def __init__(self,iamProfilename) :
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.ec2client = self.session.client('ec2')

    #Entire List of information(JSON) of Instances Filtered
    def _getInfoListofFilterdInstances(self,filtersList) :
        response = self.ec2client.describe_instances(
            Filters=filtersList
            #Filters SHOULD BE.
            )
        return(response)

    def _modifyInstanceType(self,instanceId,instanceType) :
        response = self.ec2client.modify_instance_attribute(
            InstanceId = instanceId,
            InstanceType = {
                    'Value':instanceType
                    #Instance Type References : https://aws.amazon.com/ko/ec2/instance-types/
                    }
                )
        return(response)

class Client_Iam :

    def __init__(self,iamProfilename) :
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.iamclient = self.session.client('iam')

    #load InstanceProfile
    def _getListofInstanceProfiles(self) :
        response = self.iamclient.list_instance_profiles()
        return(response)

class Client_Ssm :

    def __init__(self,iamProfilename) :
        from boto3 import Session
        self.session = Session(profile_name=iamProfilename)
        self.ssmclient = self.session.client('ssm')

    #get a simple information about a specific EC2 Instance.
    def _getSSMinfoOfInsatances(self,instanceIds) :
        #AWS CLI describe-instance-information Reference : https://docs.aws.amazon.com/cli/latest/reference/ssm/describe-instance-information.html
        response = self.ssmclient.describe_instance_information(
                            InstanceInformationFilterList = [
                                        {
                                            'key':'InstanceIds',
                                            'valueSet':instanceIds,
                                        }
                                ],
                        )
        return(response)

    #get Documents on AWS SSM to use .send_command module
    def _getListOfssmDocuments(self) :
        #What is the Document in AWS SSM? https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/sysman-ssm-docs.html
        #If you want to execute shell command in EC2 instances via boto3, you might be albe to use 'AWS-RunShellScript'.
        response = self.ssmclient.list_documents(
                            DocumentFilterList = [
                                    { 'key':'Owner', 'value':'Public' },
                                ],
                        )
        return(response)

    #Remote shell cmd execution through EC2 SSM(Async)
    def _sendCmdToSpecificInstance(self,instanceIds,documentName,serviceRoleArn,notificationArn,shellCmds,comment) :
        response = self.ssmclient.send_command(
                                #.send_command Arguments Reference : http://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html
                            InstanceIds = instanceIds,
                            DocumentName = documentName, 
                            Comment = comment,
                            Parameters = { 'commands' : shellCmds },
                            ServiceRoleArn = serviceRoleArn,
                                            #Create Role Reference : https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles_create_for-user.html
                                            #1. For using shell commands via boto3, the serviceRoleArn should have AWS SSM(.send_command module) and AWS SNS(NotificationConfig argument) access auth.
                                            #2. Role should be registered already when EC2 instance is created.
                            NotificationConfig = {
                                    #Case#02 Notification is available when the Role has AWS SNS access auth. : botocore.errorfactory.InvalidRole: An error occurred (InvalidRole) when calling the SendCommand operation: ServiceRoleArn is a required parameter to enable notification
                                    #Notification Setting Reference : http://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/rc-sns-notifications.html
                                    #Testing AWS CLI cmd : aws ssm send-command --instance-ids "<instance id>" --document-name "AWS-RunShellScript" --parameters commands="<cmd>" --service-role <iam-role-arn> --notification-config NotificationArn=<AWS-SNS-task-arn>
                                    'NotificationArn' : notificationArn,
                                    'NotificationEvents' : ['All'],
                                    'NotificationType' : 'Invocation',
                                },
                            OutputS3BucketName = 'ssmresults',
                            )

        return(response)

    #Check the shell cmd return messages after remote shell cmd execution
    def _getListofCmdResults(self,instanceId) :
        response = self.ssmclient.list_command_invocations(
                            InstanceId = instanceId,
							#EC2 Status Filter : 'InProcess', 'Success', 'Pending', 'DeliveryTimedOut', 'ExecutionTimedOut', 'Failed'
                            #Filters = [
                            #        {
                            #            'key':'Status', 'value':'InProcess',	
                            #        }
                            #    ],
                            Details = True,
                        )
        return(response)

	#Cancel the remotet cmd execution as it is still running.
    def _sendCmdToCancelinprocessCmd(self,commandId):
        response = self.ssmclient.cancel_command(
                                #.cancel_command Arguments Reference : http://boto3.readthedocs.io/en/latest/reference/services/ssm.html#SSM.Client.cancel_command
                            CommandId = commandId,
                        )
        return(response)

    #Check the shell cmd return messages with InstanceId and ComamndId
    def _getRusultsAfterSendCmd(self,commandId,instanceid) :
        response = self.ssmclient.get_command_invocation(
                            CommandId = commandId,
                            InstanceId = instanceid,
                        )
        return(response) 
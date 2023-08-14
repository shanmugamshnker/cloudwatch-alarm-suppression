import boto3
import json

cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
SNS_TOPIC_ARN = ''  # replace with your SNS Topic ARN

def handle_alarm(alarm_names, action):
    try:
        if action == "enable":
            cloudwatch.enable_alarm_actions(AlarmNames=alarm_names)
        elif action == "disable":
            cloudwatch.disable_alarm_actions(AlarmNames=alarm_names)
    except cloudwatch.exceptions.ResourceNotFound:
        return {"error": f"The following alarms do not exist: {', '.join(alarm_names)}"}

    # Notify through SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f'Alarms {", ".join(alarm_names)} have been {action}d.',
        Subject=f'CloudWatch Alarms {action.capitalize()} Notification'
    )

    # Log to CloudWatch logs
    print(f'Alarms {", ".join(alarm_names)} have been {action}d.')

def get_all_alarms():
    alarms = []
    paginator = cloudwatch.get_paginator('describe_alarms')
    for page in paginator.paginate():
        alarms.extend(page['MetricAlarms'])
    return alarms

def filter_alarms_by_tags(alarms, tag_key, tag_value):
    filtered_alarms = []
    for alarm in alarms:
        tags = cloudwatch.list_tags_for_resource(ResourceARN=alarm['AlarmArn'])['Tags']
        if any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in tags):
            filtered_alarms.append(alarm['AlarmName'])
    return filtered_alarms

def lambda_handler(event, context):
    try:
        action = event.get('action')
        if action not in ['enable', 'disable']:
            return {"error": "Invalid action. Must be either 'enable' or 'disable'."}

        alarm_names = event.get('alarmNames', [])

        services_tag_key = event.get('servicesTagKey')
        services_tag_value = event.get('servicesTagValue')
        severity_tag_key = event.get('severityTagKey')
        severity_tag_value = event.get('severityTagValue')

        if not alarm_names and not (services_tag_key or severity_tag_key):
            return {"error": "No alarm names or tags provided."}

        if alarm_names:
            if "*" in "".join(alarm_names):
                alarms = get_all_alarms()
                prefix = alarm_names[0].split('*')[0]
                alarms_to_act = [alarm['AlarmName'] for alarm in alarms if alarm['AlarmName'].startswith(prefix)]
                handle_alarm(alarms_to_act, action)
            else:
                handle_alarm(alarm_names, action)

        # Processing alarms based on tags
        if services_tag_key or severity_tag_key:
            alarms = get_all_alarms()
            
            if services_tag_key:
                alarms_to_act = filter_alarms_by_tags(alarms, services_tag_key, services_tag_value)

            if severity_tag_key:
                alarms_to_act += filter_alarms_by_tags(alarms, severity_tag_key, severity_tag_value)
                alarms_to_act = list(set(alarms_to_act))  # removing duplicates

            if alarms_to_act:
                handle_alarm(alarms_to_act, action)
            else:
                return {"message": f"No alarms found with the specified tags."}

        return {"message": f"Alarms have been {action}d successfully!"}
    except Exception as e:
        return {"error": str(e)}

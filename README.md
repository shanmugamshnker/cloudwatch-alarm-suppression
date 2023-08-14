# CloudWatch Alarm Suppressor

This tool provides a way to manage (enable/disable) CloudWatch Alarms using AWS Lambda. It provides flexibility in selecting alarms by name patterns or associated tags.

## Features:

- Enable/Disable CloudWatch alarms by providing specific names or by using a prefix.
- Use tags associated with alarms to selectively enable/disable them.
- Notify actions taken via SNS.
- Supports pagination to handle a large number of alarms.

## Requirements:

- Python 3.x
- Boto3 library
- AWS Lambda
- An SNS topic for notifications

## Setup:

1. Ensure you have the necessary permissions in AWS to describe CloudWatch alarms, modify alarm state, and publish to SNS.
2. Set up an AWS Lambda function.
3. Replace `SNS_TOPIC_ARN` in the code with your SNS Topic ARN.
4. Deploy this script to your AWS Lambda.

## How to use:

Trigger the Lambda function with an event payload that describes the action and selection criteria. Here's an example of the payload structure:

```json
{
  "action": "disable", 
  "alarmNames": ["MyAlarmName", "AnotherAlarm*"],
  "servicesTagKey": "Service",
  "servicesTagValue": "WebApp",
  "severityTagKey": "Severity",
  "severityTagValue": "Critical"
}
```

## Payload Breakdown:

- **action**: Can be either 'enable' or 'disable'.
- **alarmNames**: List of alarm names or prefixes. Use a wildcard (`*`) for prefix matching.
- **servicesTagKey** and **servicesTagValue**: Filter alarms by a specific service tag.
- **severityTagKey** and **severityTagValue**: Filter alarms by a specific severity tag.

Note: If you use both names and tags, the script will first process names and then tags.

## Contributions:

Feel free to fork this repository and make any changes or improvements you see fit. Pull requests are welcome!

## License:

This project is licensed under the Apache License 2.0. See LICENSE file for more details.

COMMANDS_ENABLED = {
    "access-keys-rotated": {
        "parameters": [{"name": "max_age", "default_value": "90", "type": "int"}],
        "class": "IAM",
        "method": "access_keys_rotated",
        "short_description": "Checks whether the active access keys are rotated within the number of days.",
    },
    "ebs-encryption": {
        "parameters": [
            {"name": "ebs_encryption", "default_value": "no", "type": "bool"}
        ],
        "class": "EC2",
        "method": "ebs_encryption",
        "short_description": "Check that Amazon Elastic Block Store (EBS) encryption is enabled by default.",
    },
    "imdsv2-check": {
        "parameters": [{"name": "imdsv2_check", "default_value": "no", "type": "bool"}],
        "class": "EC2",
        "method": "imdsv2_check",
        "short_description": "Checks Amazon EC2 instance metadata is configured with IMDSv2.",
    },
    "pitr-enabled": {
        "parameters": [{"name": "pitr_enabled", "default_value": "no", "type": "bool"}],
        "class": "DYNAMODB",
        "method": "pitr_enabled",
        "short_description": "Checks that point in time recovery is enabled for Amazon DynamoDB tables.",
    },
}

COMMANDS_ENABLED = {
    "access-keys-rotated": {
        "parameters": [{"name": "max_age", "default_value": "90", "type": "int"}],
        "class": "IAM",
        "method": "access_keys_rotated",
        "short_description": "Checks whether the active access keys are rotated within the number of days.",
    },
}

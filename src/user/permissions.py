"""This module contains classes for Permission levels
and functions for checking its label or value
"""
from enum import IntEnum


class PermissionLevel(IntEnum):
    """ Represents the Rankings of user permissions ranging from lowest to highest.
    Values:
        DEFAULT - Default permissions, no interaction allowed with this bot unless specified
        USER - Permission to execute any command
        SUPERUSER - Full permissions to use any command.
    """
    DEFAULT = 0  # The lowest default permission for any user in a server
    USER = 1  # The middle permission, allows a user to use general commands like running a script
    SUPERUSER = 2  # The highest permission, allows a user to use any command


# Permission labels corresponding to their permission
PERMISSION_LABELS = {
    'default': PermissionLevel.DEFAULT,
    'user': PermissionLevel.USER,
    'superuser': PermissionLevel.SUPERUSER
}


def get_permission_of_label(permission_label):
    """ Gets the permission value of the label
    Args:
        param permission_label (str): The name / label of the string
    :return: Permission value
        Example:
            The label of Permission.DEFAULT would be 'default'
    """
    return PERMISSION_LABELS[permission_label]


def get_label_of_permission(permission):
    """ Gets the label of the permission value
    Args:
        param permission (Permission): The permission value
    :returns: Permission label or None if no label was found
    """
    for label in PERMISSION_LABELS:
        if PERMISSION_LABELS[label] == permission:
            return label
    return None

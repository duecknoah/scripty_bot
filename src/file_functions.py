import src.user.permissions as permissions
import src.file.files as files

def id_to_user(client, id):
    """ Converts the given id to a user, returning None if that user couldn't be found
    :returns user or None
    """
    for user in client.get_all_members():
        if user.id == id:
            return user
    return None

def get_user_permission_level(user_id):
    """Returns the permission level of the user"""
    user_perms_list = files.users_file.get_data()
    for p in user_perms_list:
        if user_id in user_perms_list[p]:
            return permissions.get_permission_of_label(p[:-1])
    return permissions.PermissionLevel.DEFAULT

def set_user_permission(user_id, client, permission):
    """ Sets the user (id) to the desired permission level (permission).
    Args:
        user_id -- id of the user to set permission of
        client -- the discord client
        permission -- the permission to set the user to

    It will return a string that can be used as a
    reply message for either the console or server
    :returns str
    """
    user_to_add = id_to_user(client, user_id)  # set when id is validated
    user_is_valid = False # default

    # Validate that the user exists
    if user_to_add != None:
        user_is_valid = True

    if not user_is_valid:
        return "Invalid or non-existant user. ex. {} @exampleuser"\
            .format(permissions.get_label_of_permission(permission))

    # Check if the users permission level already is what we are trying to set it to
    current_permission = get_user_permission_level(user_id)

    if current_permission == permission:
        return "{} is already a {}".format(user_to_add.name,
                                           permissions.get_label_of_permission(permission))

    # Remove current permission if we are not currently just the default permission,
    # (the default permission users are not stored in the users file)
    # we don't want the user to have multiple permission levels
    # in the users file.
    if current_permission != permissions.PermissionLevel.DEFAULT:
        keyInFile = permissions.get_label_of_permission(current_permission) + 's'
        if user_id in files.users_file.get_data()[keyInFile]:
            files.users_file.get_data()[keyInFile].remove(user_id)

    # Set the permission of the user
    # Note that we do not add users with the default permission to the users file.
    # As the default permission means at least same permission as everyone on the server
    if permission != permissions.PermissionLevel.DEFAULT:
        permission_save_name = permissions.get_label_of_permission(permission) + 's'
        files.users_file.get_data()[permission_save_name].append(user_id)
    return "{} is now a {}".format(
        user_to_add.name,
        permissions.get_label_of_permission(permission))
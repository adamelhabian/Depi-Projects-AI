def get_entity_id(obj):
    if hasattr(obj, "person_id"):
        return obj.person_id

    elif hasattr(obj, "id"):
        return obj.id

    elif hasattr(obj, "_id"):
        return obj._id

    return "N/A"
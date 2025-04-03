from modules.model.kit_type import KitDefObject


def mk_kit_def_obj(data: dict) -> dict[str, KitDefObject]:

    res = {}

    for list_item in data:
        kit_def_obj = KitDefObject(list_item)
        res[kit_def_obj.kit_name] = kit_def_obj

    print(f"Loaded {len(res)} kits")
    return res

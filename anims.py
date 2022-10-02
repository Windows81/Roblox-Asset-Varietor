import requests


def list():
    base = (
        "https://catalog.roblox.com/v1/search/items"
        + "?category=AvatarAnimations"
        + "&subcategory=EmoteAnimations"
        + "&limit=120&cursor="
    )
    cursor = ""
    result = []
    while cursor != None:
        json = requests.get(f"{base}{cursor}").json()
        result += [item["id"] for item in json["data"]]
        cursor = json["nextPageCursor"]
    return result


def get_tag(content: bytes, prefix: bytes, suffix: bytes, offset=0):
    begin = content.index(prefix) + len(prefix) + offset
    end = content.index(suffix, begin)
    return content[begin:end]


def get_info(id):
    content = requests.get(
        f"https://assetdelivery.roblox.com/v1/asset/?id={id}"
    ).content
    is_bin = chr(content[7]) == "!"
    if is_bin:
        return {
            "anim_id": int(get_tag(content, b"roblox.com/asset/?id=", b"PROP")),
            "anim_name": get_tag(content, b"Name\x01", b"PROP", offset=4).decode(),
        }
    else:
        return {
            "anim_id": int(get_tag(content, b"roblox.com/asset/?id=", b"<")),
            "anim_name": get_tag(content, b'Name">', b"<").decode(),
        }


if __name__ == "__main__":
    l = {id: get_info(id) for id in list()}
    print(l)

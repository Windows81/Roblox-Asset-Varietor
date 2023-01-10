import requests
import json


def traverse(base) -> list[int]:
    cursor = ""
    result = []
    while cursor != None:
        json = requests.get(f"{base}{cursor}").json()
        result += [item["id"] for item in json["data"]]
        cursor = json["nextPageCursor"]
    return result


def list_emotes() -> list[int]:
    base = (
        "https://catalog.roblox.com/v1/search/items"
        + "?category=AvatarAnimations"
        + "&subcategory=EmoteAnimations"
        + "&limit=120&cursor="
    )
    return traverse(base)


def list_bundles() -> list[int]:
    base = (
        "https://catalog.roblox.com/v1/search/items"
        + "?subcategory=AnimationBundles"
        + "&limit=120&cursor="
    )
    return traverse(base)


def get_tag(content: bytes, prefix: bytes, suffix: bytes, offset=0) -> bytes:
    begin = content.index(prefix) + len(prefix) + offset
    end = content.index(suffix, begin)
    return content[begin:end]


def get_tags(content: bytes, prefix: bytes, suffix: bytes, offset=0) -> list[bytes]:
    result = []
    i_off = 0
    try:
        while True:
            begin = content.index(prefix, i_off) + len(prefix) + offset
            end = content.index(suffix, begin)
            sub = content[begin:end]
            result.append(sub)
            i_off = begin
    except ValueError:
        return result


def get_anim(iden) -> tuple[str, int]:
    content = requests.get(
        f"https://assetdelivery.roblox.com/v1/asset/?id={iden}"
    ).content
    is_bin = chr(content[7]) == "!"
    if is_bin:
        start_name = b"Name\x01"
        start_id = b"roblox.com/asset/?id="
        ends_name = [b"PROP"]
        ends_id = [b"PROP", b"/"]
    else:
        start_name = b'Name">'
        start_id = b"roblox.com/asset/?id="
        ends_name = [b"<"]
        ends_id = [b"<", b"/"]

    anim_name = None
    anim_id = None
    ctrl = b'\0\x0c\b\x11\t\r\n\\"'
    for e in ends_name:
        try:
            anim_name = get_tag(content, start_name, e).strip(ctrl).decode()
            break
        except ValueError:
            pass
    for e in ends_id:
        try:
            anim_id = int(get_tag(content, start_id, e))
            break
        except ValueError:
            pass
    return (anim_name, anim_id)


def get_bundles(iden):
    t = requests.get(f"https://web.roblox.com/bundles/{iden}").text
    names = get_tags(t, 'data-name="', '"\r\n')
    ids = get_tags(t, 'data-asset-id="', '"')
    return {n: get_anim(i)[1] for i, n in zip(ids, names)}


if __name__ == "__main__":
    emotes = {
        f"catalog/{iden}": dict([get_anim(iden)])
        for iden in list_emotes()
    }
    bundles = {
        f"bundles/{iden}": get_bundles(iden)
        for iden in list_bundles()
    }
    with open("anims.json", "w") as f:
        json.dump(bundles | emotes, f, indent="\t")
    # print(json.dumps(emotes))

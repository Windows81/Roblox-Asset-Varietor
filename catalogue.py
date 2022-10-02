import requests
import json
import os

COOKIE = os.environ.get("ROBLOSECURITY")


def page(q, cookie=COOKIE, n=0):
    return [
        d["id"]
        for d in requests.get(
            f"https://apis.roblox.com/toolbox-service/v1/marketplace/Decal?limit=1000&pageNumber={n}&keyword={q}&useCreatorWhitelist=false&includeOnlyVerifiedCreators=false&sortType=updated&sortOrder=desc",
            cookies={".ROBLOSECURITY": cookie},
        ).json()["data"]
    ]


def asset_infos(ids, cookie=COOKIE):
    return requests.get(
        f'https://apis.roblox.com/toolbox-service/v1/items/details?assetIds={",".join(str(i) for i in ids)}',
        cookies={".ROBLOSECURITY": cookie},
    ).json()["data"]


def asset_ids(q, cookie=COOKIE):
    result = []
    n = 0
    while True:
        a = page(q, cookie, n)
        if not a:
            break
        result.extend(a)
        n += 1
    return result


def info(q, cookie=COOKIE):
    N = 30
    ids = asset_ids(q, cookie)
    return [a for i in range(0, len(ids), N) for a in asset_infos(ids[i : i + N])]


if __name__ == "__main__":
    result = info("seamless")
    result.sort(key=lambda x: x["asset"]["createdUtc"], reverse=True)
    with open("catalogue.json", "w") as f:
        json.dump(result, f, indent="\t")

# $q=(curl -s "https://apis.roblox.com/toolbox-service/v1/marketplace/Decal?limit=50&pageNumber=0&keyword=seamless&useCreatorWhitelist=false&includeOnlyVerifiedCreators=false&sortType=updated&sortOrder=desc" -H "Cookie: .ROBLOSECURITY=$env:ROBLOSECURITY"|grep -Po "(?<=id.:)[0-9]+") -join ',';curl "https://apis.roblox.com/toolbox-service/v1/items/details?assetIds=$q" -H "Cookie: .ROBLOSECURITY=$env:ROBLOSECURITY"|less

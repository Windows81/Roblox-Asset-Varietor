import argparse
import requests
import json
import os

COOKIE = os.environ.get("ROBLOSECURITY")


def page(category, keyword, cookie=COOKIE, n=0) -> list[int]:
    return [
        d["id"]
        for d in requests.get(
            f"https://apis.roblox.com/toolbox-service/v1/marketplace/{category}?limit=1000&pageNumber={n}&keyword={keyword}&useCreatorWhitelist=false&includeOnlyVerifiedCreators=false&sortType=updated&sortOrder=desc",
            cookies={".ROBLOSECURITY": cookie},
        ).json()["data"]
    ]


def asset_infos(ids, cookie=COOKIE):
    return requests.get(
        f'https://apis.roblox.com/toolbox-service/v1/items/details?assetIds={",".join(str(i) for i in ids)}',
        cookies={".ROBLOSECURITY": cookie},
    ).json()["data"]


def asset_ids(category, keyword, cookie=COOKIE) -> list[int]:
    result = []
    n = 0
    while True:
        a = page(category, keyword, cookie, n)
        if not a:
            break
        result.extend(a)
        n += 1
    return result


def info(category, keyword, cookie=COOKIE):
    N = 30
    ids = asset_ids(category, keyword, cookie)
    return [a for i in range(0, len(ids), N) for a in asset_infos(ids[i: i + N])]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword", type=str, default="PBR")
    parser.add_argument("category", type=str, default="Model", nargs="?")
    parser.add_argument("filename", type=str, default="catalogue.json", nargs="?")
    parser.add_argument("cookie", type=str, default=COOKIE, nargs="?")
    args = parser.parse_args()

    result = info(category=args.category, keyword=args.keyword, cookie=args.cookie)
    result.sort(key=lambda x: x["asset"]["updatedUtc"], reverse=True)
    with open(args.filename, "w") as f:
        json.dump(result, f, indent="\t")

# $q=(curl -s "https://apis.roblox.com/toolbox-service/v1/marketplace/Decal?limit=50&pageNumber=0&keyword=seamless&useCreatorWhitelist=false&includeOnlyVerifiedCreators=false&sortType=updated&sortOrder=desc" -H "Cookie: .ROBLOSECURITY=$env:ROBLOSECURITY"|grep -Po "(?<=id.:)[0-9]+") -join ',';curl "https://apis.roblox.com/toolbox-service/v1/items/details?assetIds=$q" -H "Cookie: .ROBLOSECURITY=$env:ROBLOSECURITY"|less

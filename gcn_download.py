# need to pip install httpx rich pick

import sys
import urllib.parse
import xml.etree.cElementTree as ET
import atexit

import httpx
import rich.progress
from pick import pick


gClient : httpx.Client = None
gGamesArray : 'list[str]' = None

def exit():
    global gClient
    if gClient is not None:
        gClient.close()
    gClient = None

atexit.register(exit)

def get_games_list() -> None:
    global gClient
    global gGamesArray
    xml_url = 'https://archive.org/download/gamecubeusaredump/gamecubeusaredump_files.xml'

    if gClient is None:
        gClient = httpx.Client()

    resp = gClient.get(xml_url, follow_redirects=True)

    if resp.status_code != 200:
        print("Could not retrieve games list")
        sys.exit(1)

    tree = ET.fromstring(resp.content)
    gGamesArray = [x.get("name") for x in tree.iter() if x.get("name") is not None and "7z" in x.get("name")]


if __name__ == "__main__":
    base_url = 'https://archive.org/download/gamecubeusaredump/'

    get_games_list()

    pickTitle = 'Select game to download:'
    opt, index = pick(gGamesArray, pickTitle, indicator=">")

    game = gGamesArray[index]

    game_url = f"{base_url}/{urllib.parse.quote(game)}"
    print(f"Downloading \"{game}\"")

    with open(game, "wb") as fp, gClient.stream("GET", game_url, follow_redirects=True) as s:
        total = int(s.headers["Content-Length"])

        with rich.progress.Progress(
            "[progress.percentage]{task.percentage:>3.0f}%",
            rich.progress.BarColumn(bar_width=None),
            rich.progress.DownloadColumn(),
            rich.progress.TransferSpeedColumn(),
        ) as progress:
            download_task = progress.add_task(f"Downloading {game}", total=total)
            for chunk in s.iter_bytes():
                fp.write(chunk)
                progress.update(download_task, completed=s.num_bytes_downloaded)

    gClient.close()

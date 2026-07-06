import os
import requests
import glob
import json

def get_sprites_from_web(keys:list[str], sprite_type:str="normal", output_dir:str="imgs"):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, output_dir)
    os.makedirs(output_dir, exist_ok=True)

    pngs_paths = glob.glob(f"{output_dir}/*.png")
    already_exists = [
        os.path.splitext(os.path.basename(path))[0]
        for path in pngs_paths
    ]
    to_download = [key for key in keys if key not in already_exists]

    for key in to_download:
        urls = [
            f"https://img.pokemondb.net/sprites/lets-go-pikachu-eevee/{sprite_type}/{key}.png",
            f"https://img.pokemondb.net/sprites/sword-shield/{sprite_type}/{key}.png",
            f"https://img.pokemondb.net/sprites/items/{key}.png"
        ]
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                extension = os.path.splitext(url)[1]
                if not extension:
                    extension = ".png"

                splited_url = url.split("/")
                name = splited_url[-1].split(".")[0]
                
                filename = f"{name}_{sprite_type}{extension}" if sprite_type != "normal" else f"{name}{extension}"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"Downloading: {filename}")
                break

            except Exception as e:
                print(f"Error on {url}: {e}")

if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, "./data/data.json"), "r", encoding="utf-8") as f:
            data = json.load(f)

    sprite_list = []
    for evolution_line in data.keys():
        for stage in data[evolution_line]["stages"].values():
            if isinstance(stage, dict):
                sprite_list.append(stage["name"])

            elif isinstance(stage, list):
                for i in range(len(stage)):
                    sprite_list.append(stage[i]["name"])

    sprite_list.append("poke-ball")
    get_sprites_from_web(keys=sprite_list)
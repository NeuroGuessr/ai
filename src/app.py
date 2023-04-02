from fastapi import FastAPI
from ImageCollector import ImageCollector
from fastapi.staticfiles import StaticFiles
from random import shuffle, sample
from copy import deepcopy
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def root():
    return "Up and running"

@app.get("/{key}")
async def pass_key(key: str):
    if key == "key":
        pass
    
@app.get("/image/{game_id}")
async def serve_games(game_id: int):
    image_collector = ImageCollector()
    image_collector.load_data()
    pairs = image_collector.filter_images(111)
    
    
    images = sample(list(zip(pairs.keys(), pairs.values())), 12)
    correct = [images[4*stage:4*(stage+1)] for stage in range(3)]
    labels = [correct[stage][i][1] for stage in range(3) for i in range(4)]
    shuffle(labels)
    print(images)
    print(correct)
    
    content = [
        {
            'images': [correct[stage][i][0] for i in range(4)],
            'labels': labels,
            'correct': {
                correct[stage][i][0] : correct[stage][i][1] for i in range(4)
            }
        }
        for stage in range(3)
    ]
    
    return json.dumps(content)
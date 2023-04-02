from fastapi import FastAPI
from ImageCollector import ImageCollector
from fastapi.staticfiles import StaticFiles
from random import shuffle, sample
import json
from pydantic import BaseModel
from CategoryManager import CategoryManager

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

category_manager = CategoryManager()
image_collector = ImageCollector(category_manager)
image_collector.load_data()

class Category(BaseModel):
    stages: int
    stage_batch_size: int

@app.get("/")
async def root():
    return "Up and running"

# @app.get("/{key}")
# async def pass_key(key: str):
#     if key == "key":
#         pass
    
@app.get("/category")
async def list_categories():
    return json.dumps(category_manager.get_categories())

@app.post("/category/{key}")
async def serve_games(key: str, game_info: Category):
    stages = game_info.stages
    per_stage = game_info.stage_batch_size
    
    pairs = image_collector.filter_images(key)
    
    images = sample(list(zip(pairs.keys(), pairs.values())), stages*per_stage)
    correct = [images[per_stage*stage:per_stage*(stage+1)] for stage in range(stages)]
    labels = [correct[stage][i][1] for stage in range(stages) for i in range(per_stage)]
    shuffle(labels)
    
    content = [
        {
            'images': [correct[stage][i][0] for i in range(per_stage)],
            'labels': labels,
            'correct': {
                correct[stage][i][0] : correct[stage][i][1] for i in range(per_stage)
            }
        }
        for stage in range(stages)
    ]
    
    return json.dumps(content)
from fastapi import FastAPI, HTTPException
from ImageCollector import ImageCollector
from fastapi.staticfiles import StaticFiles
from random import shuffle, sample, choice
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
    
@app.get("/category")
async def list_categories():
    return json.dumps(category_manager.get_categories())

@app.post("/category/random")
async def serve_random_category(game_info: Category):
    stages = game_info.stages
    per_stage = game_info.stage_batch_size
    
    key = choice(list(category_manager.get_categories().keys()))
    
    pairs = image_collector.filter_images(key)
    
    if len(pairs) < stages*per_stage:
        raise HTTPException(status_code=418, detail="requested too many images!")
    
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

@app.post("/category/{key}")
async def serve_games(key: str, game_info: Category):
    stages = game_info.stages
    per_stage = game_info.stage_batch_size
    
    pairs = image_collector.filter_images(key)
    
    if len(pairs) < stages*per_stage:
        raise HTTPException(status_code=418, detail="requested too many images!")
    
    images = sample(list(zip(pairs.keys(), pairs.values())), stages*per_stage)
    # print(len(images))
    correct = [images[per_stage*stage:per_stage*(stage+1)] for stage in range(stages)]
    # print(len(correct))
    labels = [[correct[stage][i][1] for i in range(per_stage)] for stage in range(stages)]
    # print(len(labels))
    for i in range(stages):
        temp = labels[i]
        shuffle(temp)
        labels[i] = temp
    
    # print(labels)
    content = [
        {
            'images': [correct[stage][i][0] for i in range(per_stage)],
            'labels': labels[stage],
            'correct': {
                correct[stage][i][0] : correct[stage][i][1] for i in range(per_stage)
            }
        }
        for stage in range(stages)
    ]
    
    return json.dumps(content)
import os

class ImageCollector:
    def __init__(self):
        self.correct = {} # name -> label
    
    def filter_images(self, key):
        return self.correct
    
    def load_data(self):
        with open("../static/labels.txt", 'r') as file:
            for pair in [line.replace('\n', "").split(":") for line in file]:
                self.correct[pair[0] + ".jpg"] = pair[1]
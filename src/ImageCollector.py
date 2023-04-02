import os
from CategoryManager import CategoryManager

class ImageCollector:
    def __init__(self, category_manager: CategoryManager):
        self.category_manager = category_manager
        self.correct = {} # name -> label
    
    def filter_images(self, key: str) -> dict:
        category_uuid = self.category_manager.get_categories()[key]
        return {key + "/" + image: self.correct[key + "/" + image] for image in self.category_manager.get_images(category_uuid)}
    
    def load_data(self):
        with open("../static/index.txt", 'r') as file:
            for triplet in [line.replace('\n', "").split(":") for line in file]:
                self.correct[triplet[0] + "/" + triplet[1] + ".jpg"] = triplet[2]
                if triplet[0] not in self.category_manager.get_categories().keys():
                    self.category_manager.add_category(triplet[0])
                category_uuid = self.category_manager.get_categories()[triplet[0]]
                self.category_manager.tag_image(triplet[1] + ".jpg", category_uuid)
                
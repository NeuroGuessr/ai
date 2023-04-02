from uuid import uuid4

class CategoryManager:
    def __init__(self):
        self.categories = {} # category_id -> category name
        self.images = {} # category_id -> image list

    def get_categories(self) -> dict:
        return self.categories

    def get_category_uuid(self, category_name: str):
        for key, value in self.categories.items():
            if value == category_name:
                return key

    def get_images(self, category_uuid: str) -> list:
        return self.images[category_uuid]

    def tag_image(self, image: str, category_name: str):
        self.images[category_name].append(image)

    def add_category(self, name: str):
        category_uuid = str(uuid4())
        self.categories[category_uuid] = name
        self.images[category_uuid] = []
        
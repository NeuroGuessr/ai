import openai, random
openai.api_key = "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"


def filter_out_sc(input:str)->str:
        special_characters=['@','#','$','*','&',"""\n""",'"','\\',"",":","(",")","[","]"]
        for char in special_characters:
            input = input.replace(char,"")
        return input
assert filter_out_sc(""" "string alallal \ dafs \n special""") == " string alallal  dafs  special"
   
class BasePromptGenerator():
   
    decorator_keywords = ["digital painting", "hyperrealistic", "fantasy", "Surrealist", "full body"," artstation", "highly detailed", "sharp focus", "sci-fi", "stunningly beautiful", "dystopian", "iridescent gold", "cinematic lighting", "dark"]
    def random_decorators(self,n:int)-> str:
        if n<=0:
            return ""
        return ",".join(random.choices(self.decorator_keywords,k=n)) 
    
    def send_gpt_request(self,system_rules:str,user_prompt:str, n_sentences:int, randomness_temperature:float=1.0, accuracy_filter:float=1.0, max_tokens:int=10):
        #print("type:{} content:{}".format(type(user_prompt),user_prompt))
        #print("type:{} content:{}".format(type(system_rules),system_rules))
        resp =  openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[ 
                    {"role": "system", "content":system_rules},
                    {"role": "user", "content":user_prompt}
                ],
                temperature=randomness_temperature,
                top_p=accuracy_filter,
                n=n_sentences,
                max_tokens=max_tokens
        )
        #print(resp)
        return resp
class RegularPromptGenerator(BasePromptGenerator):
    def __init__(self,response_type_specifier:str="prompt text"):
        self.response_type_specifier = response_type_specifier
        self.system_rules = "{} should be around 7 words long response should include a subject (person, object, or location) and descriptors (adverbs and adjectives that describe the subject).Avoid using abstract concepts in spite of concrete nouns. Responses whould be in simple english. Avoid adding request context".format(self.response_type_specifier)
    
    def generate(self,category:str,  n_sentences:int, n_extra_decorator_keywords:int=2, randomness_temperature:float=1.0, accuracy_filter:float=1.0, max_tokens:int=10) -> list[str]:
        user_prompt = 'generate random {} as instructed by system for image generation in category:"{}"'.format(self.response_type_specifier,category)
        system_rules = "You are a helpful assistant that generates random {} in the given category to be used for image generation. {}".format(self.response_type_specifier,self.system_rules)
        response = self.send_gpt_request(system_rules=system_rules,user_prompt=user_prompt,n_sentences=n_sentences,randomness_temperature=randomness_temperature,accuracy_filter=accuracy_filter,max_tokens=max_tokens)
        sentences =[]
        try:
            for i in response["choices"]:
                sentences.append("{}{}".format(filter_out_sc(i["message"]["content"]),self.random_decorators( n_extra_decorator_keywords )))
        except:
            print("Extracting JSON response failed:")
            print(response)
        return sentences
    

class BlendPromptGenerator(BasePromptGenerator):
    def __init__(self):
        self.response_type_specifier = "object"
        self.system_rules = "Print out randomly chosen name of animal or person or object in given category. Your response should only contain that one chosen entity."
    def blend_objects(self,a_name:str, b_name:str, ratio:float):
        return "[{}:{}:{}]".format(a_name,b_name,ratio)
    def generate_keywords_from_category(self, category: str, n_sentences: int, randomness_temperature: float = 1, accuracy_filter: float = 1, max_tokens: int = 4) -> list[str]:
        user_prompt = 'generate random {} as instructed by system for image generation in category:"{}"'.format(self.response_type_specifier,category)
        system_rules = "You are a helpful assistant that generates random {} in the given category to be used for image generation. {}".format(self.response_type_specifier,self.system_rules)
        response = self.send_gpt_request(system_rules=system_rules,user_prompt=user_prompt,n_sentences=n_sentences,randomness_temperature=randomness_temperature,accuracy_filter=accuracy_filter,max_tokens=max_tokens)
        sentences =[]
        try:
            for i in response["choices"]:
                sentences.append(filter_out_sc(i["message"]["content"]))
        except:
            print("Extracting JSON response failed:")
            print(response)
        return sentences
    
    def generate(self,categories: list[str], n_sentences: int, n_extra_decorator_keywords: int = 2, randomness_temperature: float = 1, accuracy_filter: float = 1, max_tokens: int = 4) -> list[str]:
        if len(categories)<=1 :
            print("Incorrect size of categories for that method. If you want just one category use RegularPromptGenerator instead")
            return ""
        objects= []
        for i in categories:
            objects += self.generate_keywords_from_category(i,n_sentences,randomness_temperature,accuracy_filter,max_tokens)
        
        random.shuffle(objects)
        output = []
        for i in range(n_sentences):
            output.append(self.blend_objects(objects.pop(),objects.pop(),(random.random()-0.5)*0.5+0.5)) 
        
        return output                        

def test():
    reg_prompt = RegularPromptGenerator()
    blend_prompt = BlendPromptGenerator()

    print("regular prompt")
    for i in reg_prompt.generate("coconuts", 30):
        print(i)
        
    print("blend prompt")
    for i in blend_prompt.generate(["marvel universe","polish politicans"], 30):
        print(i)
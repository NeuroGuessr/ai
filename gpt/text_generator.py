import openai

openai.api_key = "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"

category = "frogs"
n_sentences = 4


def filter_out_sc(input: str) -> str:
    special_characters = ["@", "#", "$", "*", "&", """\n""", '"', "\\", ""]
    for char in special_characters:
        input = input.replace(char, "")
    return input


class PromptGenerator:
    def __init__(self, response_type_specifier: str = "prompt text"):
        self.response_type_specifier = response_type_specifier
        self.system_rules = "{} should be around 7 words long response should include a subject (person, object, or location) and descriptors (adverbs and adjectives that describe the subject).Avoid using abstract concepts in spite of concrete nouns. Responses whould be in simple english. Avoid adding request context".format(
            self.response_type_specifier
        )

    def generatePrompt(
        self,
        category: str,
        n_sentences: int,
        randomness_temperature: float = 1.0,
        accuracy_filter: float = 1.0,
        max_tokens: int = 10,
    ) -> list[str]:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates random {} in the given category to be used for image generation. {}".format(
                        self.response_type_specifier, self.system_rules
                    ),
                },
                {
                    "role": "user",
                    "content": 'generate random {} as instructed by system for image generation in category:"{}"'.format(
                        self.response_type_specifier, category
                    ),
                },
            ],
            temperature=randomness_temperature,
            top_p=accuracy_filter,
            n=n_sentences,
            max_tokens=10,
        )
        sentences = []
        try:
            for i in response["choices"]:
                sentences.append(filter_out_sc(i["message"]["content"]))
        except:
            print("Extracting JSON response failed:")
            print(response)
        return sentences

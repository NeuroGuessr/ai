from diffusion_gen.stable_diffusion_module import (
    DiffusionImageGenerator,
    image_grid,
)
from gpt.text_generator import BasePromptGenerator


def ai_loop(image_generator, prompt_generator):
    while True:
        keyword = input("Give me a category: ")
        prompt_list = prompt_generator.generatePrompt(keyword, 12)
        images = []
        for prompt in prompt_list:
            images.append(*image_generator.run(prompt))
        yield images


if __name__ == "__main__":
    image_generator = DiffusionImageGenerator()
    prompt_generator = BasePromptGenerator()
    for gen_img in ai_loop(image_generator, prompt_generator):
        image_grid(gen_img)

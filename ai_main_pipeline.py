from diffusion_gen.stable_diffusion_module import (
    DiffusionImageGenerator,
    image_grid,
)
from gpt.text_generator import PromptGenerator


def ai_loop(image_generator, prompt_generator):
    while True:
        keyword = input("Give me a category: ")
        prompt_list = prompt_generator.generatePrompt(keyword, 1)
        for prompt in prompt_list:
            image = image_generator.run(prompt)
            yield image


if __name__ == "__main__":
    image_generator = DiffusionImageGenerator()
    prompt_generator = PromptGenerator()
    for gen_img in ai_loop(image_generator, prompt_generator):
        image_grid(gen_img)

from time import time

import accelerate
import gc
import matplotlib.pyplot as plt
import numpy as np
import torch

from diffusers import DiffusionPipeline, StableDiffusionPipeline
from mpl_toolkits.axes_grid1 import ImageGrid


class DiffusionImageGenerator:
    def __init__(self):
        self.inference_steps = 40
        self.inference_alpha = 0.05
        self.mean_time = 0
        self.mean_alpha = 0.1
        self.epsilon = 4
        self.bottom_limit_inference_steps = 25
        self.upper_limit_inference_steps = 60
        self.mean_time_memory = []
        self.negative_prompt = (
            "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, "
            "extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, "
            "cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
        )

        self.pipeline = DiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5"
        )

        # Disable NSFW filter
        self.pipeline.safety_checker = lambda images, clip_input: (
            images,
            False,
        )
        if torch.cuda.is_available():
            print("Using cuda device")
            self.pipeline.to("cuda")

    def image_generation(
        self, sd_pipeline: StableDiffusionPipeline, prompt: str
    ):
        start = time()
        generated_images = sd_pipeline(
            prompt=prompt,
            negative_prompt=self.negative_prompt,
            height=400,
            width=400,
            num_inference_steps=self.inference_steps,
            num_images_per_prompt=4,
        ).images

        end = time()

        inference_time = end - start
        return generated_images, inference_time

    def run(self, prompt: str) -> np.ndarray:
        if len(self.mean_time_memory) == 5:
            self.mean_time = sum(self.mean_time_memory) / len(
                self.mean_time_memory
            )
        elif len(self.mean_time_memory) > 10:
            self.mean_time = (
                self.mean_time * (1 - self.mean_alpha)
                + self.mean_alpha * self.mean_time_memory[-1]
            )

        print(f"MEAN_TIME = {self.mean_time}")
        print(f"INFERENCE_STEPS = {self.inference_steps}")

        images, inference_time = self.image_generation(self.pipeline, prompt)

        # Update mean_time and inference steps
        if len(self.mean_time_memory) == 5:
            self.mean_time_memory.pop(0)
        self.mean_time_memory.append(inference_time)

        if self.mean_time != 0:
            if inference_time + self.epsilon > self.mean_time:
                self.inference_steps *= 1 - self.inference_alpha
            elif inference_time - self.epsilon < self.mean_time:
                self.inference_steps *= 1 + self.inference_alpha
            self.inference_steps = int(
                np.clip(
                    self.inference_steps,
                    self.bottom_limit_inference_steps,
                    self.upper_limit_inference_steps,
                )
            )

        with torch.no_grad():
            torch.cuda.empty_cache()
        gc.collect()

        return images


def image_grid(images):
    fig = plt.figure(figsize=(4.0, 4.0))
    grid = ImageGrid(
        fig,
        111,  # similar to subplot(111)
        nrows_ncols=(2, 2),  # creates 2x2 grid of axes
        axes_pad=0.1,  # pad between axes in inch.
    )
    for ax, im in zip(grid, images):
        ax.imshow(im)
    plt.show()


if __name__ == "__main__":
    generator = DiffusionImageGenerator()
    while True:
        prompt = input("Enter prompt: ")
        if prompt == "QUIT":
            break
        images = generator.run(prompt)
        image_grid(images)

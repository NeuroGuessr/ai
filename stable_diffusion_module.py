from time import time

import accelerate
import gc
import matplotlib.pyplot as plt
import numpy as np
import torch

from diffusers import DiffusionPipeline, StableDiffusionPipeline
from mpl_toolkits.axes_grid1 import ImageGrid


INFERENCE_STEPS = 40
INFERENCE_ALPHA = 0.05
MEAN_TIME = 0
MEAN_ALPHA = 0.1
EPSILON = 4
BOTTOM_LIMIT_INFERENCE_STEPS = 25
UPPER_LIMIT_INFERENCE_STEPS = 60
mean_time_memory = []
negative_prompt = (
    "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, "
    "extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, "
    "cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
)


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


def image_generation(sd_pipeline: StableDiffusionPipeline, prompt: str):
    global mean_time_memory, INFERENCE_STEPS, INFERENCE_ALPHA, MEAN_TIME, EPSILON, negative_prompt

    start = time()
    generated_images = sd_pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=400,
        width=400,
        num_inference_steps=INFERENCE_STEPS,
        num_images_per_prompt=4,
    ).images

    end = time()

    inference_time = end - start
    return generated_images, inference_time


def generation_loop(sd_pipeline: StableDiffusionPipeline) -> np.ndarray:
    global MEAN_TIME, MEAN_ALPHA, INFERENCE_STEPS, mean_time_memory

    while True:
        if len(mean_time_memory) == 5:
            MEAN_TIME = sum(mean_time_memory) / len(mean_time_memory)
        elif len(mean_time_memory) > 10:
            MEAN_TIME = (
                MEAN_TIME * (1 - MEAN_ALPHA)
                + MEAN_ALPHA * mean_time_memory[-1]
            )

        print(f"MEAN_TIME = {MEAN_TIME}")
        print(f"INFERENCE_STEPS = {INFERENCE_STEPS}")

        prompt = input("Enter prompt: ")

        if prompt == "QUIT":
            return

        images, inference_time = image_generation(sd_pipeline, prompt)

        yield images
        del images

        # Update mean_time and inference steps
        if len(mean_time_memory) == 5:
            mean_time_memory.pop(0)
        mean_time_memory.append(inference_time)

        if MEAN_TIME != 0:
            if inference_time + EPSILON > MEAN_TIME:
                INFERENCE_STEPS *= 1 - INFERENCE_ALPHA
            elif inference_time - EPSILON < MEAN_TIME:
                INFERENCE_STEPS *= 1 + INFERENCE_ALPHA
            INFERENCE_STEPS = int(
                np.clip(
                    INFERENCE_STEPS,
                    BOTTOM_LIMIT_INFERENCE_STEPS,
                    UPPER_LIMIT_INFERENCE_STEPS,
                )
            )

        with torch.no_grad():
            torch.cuda.empty_cache()
        gc.collect()


if __name__ == "__main__":
    pipeline = DiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5"
    )
    pipeline.safety_checker = lambda images, clip_input: (
        images,
        False,
    )  # Disable NSFW filter
    if torch.cuda.is_available():
        print("Using cuda device")
        pipeline.to("cuda")
    pipeline_flag = True

    for images in generation_loop(pipeline):
        image_grid(images)

# Installing and Using Custom Scripts
To install custom scripts, place them into the `scripts` directory and restart the web ui. Custom scripts will appear in the lower-left dropdown menu on the txt2img and img2img tabs after being installed. Below are some notable custom scripts created by Web UI users:

# Custom Scripts from Users

## Advanced prompt matrix
https://github.com/GRMrGecko/stable-diffusion-webui-automatic/blob/advanced_matrix/scripts/advanced_prompt_matrix.py

It allows a matrix prompt as follows:
`<cyber|cyborg|> cat <photo|image|artistic photo|oil painting> in a <car|boat|cyber city>`

Does not actually draw a matrix, just produces pictures.

## Wildcards
https://github.com/jtkelm2/stable-diffusion-webui-1/blob/master/scripts/wildcards.py

Script support so that prompts can contain wildcard terms (indicated by surrounding double underscores), with values instantiated randomly from the corresponding .txt file in the folder `/scripts/wildcards/`. For example:

`a woman at a cafe by __artist__ and __artist__`

will draw two random artists from `artist.txt`. This works independently on each prompt, so that one can e.g. generate a batch of 100 images with the same prompt input using wildcards, and each output will have unique artists (or styles, or genres, or anything that the user creates their own .txt file for) attached to it.

(also see https://github.com/jtkelm2/stable-diffusion-webui-1/tree/master/scripts/wildcards for examples of custom lists)

## txt2img2img 
https://github.com/ThereforeGames/txt2img2img/blob/main/scripts/txt2img2img.py

Greatly improve the editability of any character/subject while retaining their likeness.

Full description in original repo: https://github.com/ThereforeGames/txt2img2img (be careful with cloning as it has a bit of venv checked in)

## txt2mask
https://github.com/ThereforeGames/txt2mask

Allows you to specify an inpainting mask with text, as opposed to the brush.

## Mask drawing UI
https://github.com/dfaker/stable-diffusion-webui-cv2-external-masking-script/blob/main/external_masking.py

Provides a local popup window powered by CV2 that allows addition of a mask before processing. [Readme](https://github.com/dfaker/stable-diffusion-webui-cv2-external-masking-script).

## Img2img Video
https://github.com/memes-forever/Stable-diffusion-webui-video

Using img2img, generates pictures one after another.

## Seed Travel
https://github.com/yownas/seed_travel

Pick two (or more) seeds and generate a sequence of images interpolating between them. Optionally, let it create a video of the result.

Example of what you can do with it:
https://www.youtube.com/watch?v=4c71iUclY4U

## Saving steps of the sampling process
This script will save steps of the sampling process to a directory.
```python
import os.path

import modules.scripts as scripts
import gradio as gr

from modules import sd_samplers, shared
from modules.processing import Processed, process_images


class Script(scripts.Script):
    def title(self):
        return "Save steps of the sampling process to files"

    def ui(self, is_img2img):
        path = gr.Textbox(label="Save images to path")
        return [path]

    def run(self, p, path):
        index = [0]

        def store_latent(x):
            image = shared.state.current_image = sd_samplers.sample_to_image(x)
            image.save(os.path.join(path, f"sample-{index[0]:05}.png"))
            index[0] += 1
            fun(x)

        fun = sd_samplers.store_latent
        sd_samplers.store_latent = store_latent

        try:
            proc = process_images(p)
        finally:
            sd_samplers.store_latent = fun

        return Processed(p, proc.images, p.seed, "")
```
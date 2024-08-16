# %%
from diffusers import AutoPipelineForText2Image
import torch
import unicodedata
import re
import sys
from time import time

args = sys.argv[1:]

prompt = args[0]
# prompt = "Food photography, studio photography,burger patty,focus on the delicious patty, vibrant toppings, vegetables,natural colors, natural features."

def slugify(value, allow_unicode=True):
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
        value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
        return re.sub('[-\s]+', '-', value, flags=re.U)[:100]
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)[:100]

pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("cuda")

inf = int(args[1]) if len(args) >= 2 else 1
guidance = float(args[2]) if len(args) >= 3 else 1.0

print(f"{prompt} -> # Inference: {inf} | Guidance: {guidance}")

start = time()
image = pipe(prompt=prompt, num_inference_steps=inf, guidance_scale=guidance).images[0]
end = time()
delta = end - start
print(f"Generated in {delta:.2f} seconds -> ~{delta/60:.0f} minutes")


filename = slugify(prompt) + ".png"
image.save(filename)

print(f"Saved on {filename}")


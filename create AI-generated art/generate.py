import os
import torch
from diffusers import StableDiffusionPipeline
from datetime import datetime
import random
import csv
from tqdm import tqdm

# Set up device
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model(model_id="runwayml/stable-diffusion-v1-5"):
    """Load the Stable Diffusion model with authentication if needed."""
    # Note: Set HF_TOKEN environment variable or pass token directly
    token = os.getenv("HF_TOKEN")
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        use_auth_token=token,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe = pipe.to(device)
    if device == "cuda":
        pipe.enable_attention_slicing()  # Optimize memory usage
    return pipe

def read_prompts(prompt_file="prompts.txt"):
    """Read prompts from a text file."""
    prompts = []
    with open(prompt_file, "r") as f:
        for line in f:
            prompt = line.strip()
            if prompt:
                prompts.append(prompt)
    return prompts

def generate_image(pipe, prompt, seed, output_dir="outputs"):
    """Generate a single image with the given prompt and seed."""
    generator = torch.Generator(device=device).manual_seed(seed)
    image = pipe(
        prompt,
        height=512,
        width=512,
        num_inference_steps=50,
        guidance_scale=7.5,
        generator=generator
    ).images[0]
    return image

def save_image(image, index, output_dir="outputs"):
    """Save the generated image with a numbered filename."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"image_{index:04d}_{timestamp}.png")
    image.save(filename)
    return filename

def main():
    """Generate 50 unique images using varied prompts and random seeds."""
    model_id = "runwayml/stable-diffusion-v1-5"
    output_dir = "outputs"
    num_images = 50
    batch_size = 5  # Process in batches to manage memory

    # Load prompts
    prompts = read_prompts()
    if len(prompts) < num_images:
        print(f"Warning: Only {len(prompts)} prompts available, repeating as needed.")

    # Load model
    try:
        pipe = load_model(model_id)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Generate images in batches
    for batch_start in tqdm(range(0, num_images, batch_size), desc="Generating images"):
        batch_end = min(batch_start + batch_size, num_images)
        for i in range(batch_start, batch_end):
            prompt = random.choice(prompts)  # Randomly select a prompt
            seed = random.randint(0, 2**32 - 1)  # Random seed for uniqueness
            try:
                image = generate_image(pipe, prompt, seed, output_dir)
                save_image(image, i, output_dir)
            except Exception as e:
                print(f"Error generating image {i}: {e}")
                continue

if __name__ == "__main__":
    main()
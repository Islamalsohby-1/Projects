from flask import Flask, request, render_template
import os
import torch
from diffusers import StableDiffusionPipeline
import random
from datetime import datetime

app = Flask(__name__)

# Set up device
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model(model_id="runwayml/stable-diffusion-v1-5"):
    """Load the Stable Diffusion model."""
    token = os.getenv("HF_TOKEN")
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        use_auth_token=token,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe = pipe.to(device)
    if device == "cuda":
        pipe.enable_attention_slicing()
    return pipe

pipe = load_model()

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if prompt:
            seed = random.randint(0, 2**32 - 1)
            generator = torch.Generator(device=device).manual_seed(seed)
            try:
                image = pipe(
                    prompt,
                    height=512,
                    width=512,
                    num_inference_steps=50,
                    guidance_scale=7.5,
                    generator=generator
                ).images[0]
                output_dir = "static/outputs"
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.png"
                filepath = os.path.join(output_dir, filename)
                image.save(filepath)
                images.append(f"outputs/{filename}")
            except Exception as e:
                return f"Error generating image: {e}"
    return render_template("index.html", images=images)

if __name__ == "__main__":
    app.run(debug=True)
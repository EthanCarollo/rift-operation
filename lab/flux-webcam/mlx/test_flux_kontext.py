from mflux.models.flux.variants.txt2img.flux import Flux1

# Load the model
flux = Flux1.from_name(
   model_name="schnell",  # "schnell", "dev", or "krea-dev"
   quantize=3,            # 3, 4, 5, 6, or 8
)

# Generate an image
image = flux.generate_image(
   seed=2,
   prompt="Luxury food photograph",
   num_inference_steps=2,  # "schnell" works well with 2-4 steps, "dev" and "krea-dev" work well with 20-25 steps
   height=1024,
   width=1024,
)

image.save(path="image.png")
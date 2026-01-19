import torch
from diffusers import Flux2KleinPipeline, FluxTransformer2DModel, GGUFQuantizationConfig

torch.mps.set_per_process_memory_fraction(0.0)

prompt = "a moonim dressed as a knight, riding a horse towards a medieval castle"

ckpt_path = "/Users/ethew/Documents/Github/iotm1/lab/flux-gguf/flux-2-klein-4b-Q2_K.gguf"

transformer = FluxTransformer2DModel.from_single_file(
    ckpt_path,
    quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
    torch_dtype=torch.bfloat16,
)

pipeline = Flux2KleinPipeline.from_pretrained(
    "black-forest-labs/FLUX.2-klein-4B",
    transformer=transformer,
    torch_dtype=torch.bfloat16,
).to("mps")

height, width = 1024, 1024

images = pipeline(
    prompt=prompt,
    num_inference_steps=4,
    guidance_scale=5.0,
    height=height,
    width=width,
    generator=torch.Generator("mps").manual_seed(42)
).images[0]

images.save("gguf_image.png")

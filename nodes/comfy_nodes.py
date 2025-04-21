import os
import sys
import torch
import folder_paths
from PIL import Image
import numpy as np


# Add the parent directory to the Python path so we can import from easycontrol
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from InstantCharacter.pipeline import InstantCharacterFluxPipeline
from huggingface_hub import login


if "ipadapter" not in folder_paths.folder_names_and_paths:
    current_paths = [os.path.join(folder_paths.models_dir, "ipadapter")]
else:
    current_paths, _ = folder_paths.folder_names_and_paths["ipadapter"]
folder_paths.folder_names_and_paths["ipadapter"] = (current_paths, folder_paths.supported_pt_extensions)


class InstantCharacterLoadModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # "hf_token": ("STRING", {"default": "", "multiline": True}),
                "base_model_path": ("STRING", {"default": "/root/autodl-tmp/.cache/FLUX.1-dev", "multiline": True}),
                "image_encoder_path": ("STRING", {"default": "/root/autodl-tmp/.cache/Siglip-so400m-patch14-384", "multiline": True}),
                "image_encoder_2_path": ("STRING", {"default": "/root/autodl-tmp/.cache/Dinov2-giant", "multiline": True}),
                "ip_adapter_name": (folder_paths.get_filename_list("ipadapter"), ),
                "cpu_offload": ("BOOLEAN", {"default": False})
            }
        }
    
    RETURN_TYPES = ("INSTANTCHAR_PIPE",)
    FUNCTION = "load_model"
    CATEGORY = "InstantCharacter"

    def load_model(self, base_model_path, image_encoder_path, image_encoder_2_path, ip_adapter_name, cpu_offload):
        # login(token=hf_token)
        base_model = base_model_path
        image_encoder_path = image_encoder_path
        image_encoder_2_path = image_encoder_2_path
        cache_dir = folder_paths.get_folder_paths("diffusers")[0]
        image_encoder_cache_dir = folder_paths.get_folder_paths("clip_vision")[0]
        image_encoder_2_cache_dir = folder_paths.get_folder_paths("clip_vision")[0]
        device = "cuda" if torch.cuda.is_available() else "cpu"
        ip_adapter_path = folder_paths.get_full_path("ipadapter", ip_adapter_name)
        
        pipe = InstantCharacterFluxPipeline.from_pretrained(
            base_model, 
            torch_dtype=torch.bfloat16,
            cache_dir=cache_dir,    
        )
        if cpu_offload:
            pipe.enable_sequential_cpu_offload()
        else:
            pipe.to(device)
        
        pipe.init_adapter(
            image_encoder_path=image_encoder_path,
            cache_dir=image_encoder_cache_dir,
            image_encoder_2_path=image_encoder_2_path,
            cache_dir_2=image_encoder_2_cache_dir,
            subject_ipadapter_cfg=dict(
                subject_ip_adapter_path=ip_adapter_path,
                nb_token=1024
            ),
        )
        
        return (pipe,)


class InstantCharacterGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pipe": ("INSTANTCHAR_PIPE",),
                "prompt": ("STRING", {"multiline": True}),
                "height": ("INT", {"default": 768, "min": 256, "max": 2048, "step": 64}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 64}),
                "guidance_scale": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 10.0, "step": 0.1}),
                "num_inference_steps": ("INT", {"default": 28, "min": 1, "max": 100, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "subject_scale": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "subject_image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "InstantCharacter"

    def generate(self, pipe, prompt, height, width, guidance_scale, 
                num_inference_steps, seed, subject_scale, subject_image=None):
        
        # Convert subject image from tensor to PIL if provided
        subject_image_pil = None
        if subject_image is not None:
            if isinstance(subject_image, torch.Tensor):
                if subject_image.dim() == 4:  # [batch, height, width, channels]
                    img = subject_image[0].cpu().numpy()
                else:  # [height, width, channels]
                    img = subject_image.cpu().numpy()
                subject_image_pil = Image.fromarray((img * 255).astype(np.uint8))
            elif isinstance(subject_image, np.ndarray):
                subject_image_pil = Image.fromarray((subject_image * 255).astype(np.uint8))
        
        # Generate image
        output = pipe(
            prompt=prompt,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=torch.Generator("cpu").manual_seed(seed),
            subject_image=subject_image_pil,
            subject_scale=subject_scale,
        )
        
        # Convert PIL image to tensor format
        image = np.array(output.images[0]) / 255.0
        image = torch.from_numpy(image).float()
        
        # Add batch dimension if needed
        if image.dim() == 3:
            image = image.unsqueeze(0)
        
        return (image,)


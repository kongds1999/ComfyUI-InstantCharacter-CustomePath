Written in the front

写在前面


This is a simple modified version based on `ComfyUI-InstantCharacter`, mainly suitable for friends who have already configured the model environment locally.

这是一个基于 `ComfyUI-InstantCharacter` 的简单修改版，主要适用于本地已经配置了模型环境的小伙伴。


You can directly modify the folder paths of `Flux`, `Siglip`, and `Dinov2`, where the path of `instantcharacter_ip-adapter.bin` is

你可以直接修改 `Flux`、`Siglip`、和`Dinov2`的文件夹路径，其中 `instantcharacter_ip-adapter.bin`路径为
```
/path/to/ComfyUI/models/ipadapter/instantcharacter_ip-adapter.bin
```
![](./assets/node.png)

Note that `path` is the address of the local model repository, not the address of a single file, such as
注意，`path`为本地模型仓库的地址，不是单个文件的地址，如
```
/root/autodl-tmp/.cache/FLUX.1-dev/
.
├── LICENSE.md
├── README.md
├── ae.safetensors
├── configuration.json
├── dev_grid.jpg
├── flux1-dev.safetensors
├── model_index.json
├── scheduler
│   └── scheduler_config.json
├── text_encoder
│   ├── config.json
│   └── model.safetensors
├── text_encoder_2
│   ├── config.json
│   ├── model-00001-of-00002.safetensors
│   ├── model-00002-of-00002.safetensors
│   └── model.safetensors.index.json
├── tokenizer
│   ├── merges.txt
│   ├── special_tokens_map.json
│   ├── tokenizer_config.json
│   └── vocab.json
├── tokenizer_2
│   ├── special_tokens_map.json
│   ├── spiece.model
│   ├── tokenizer.json
│   └── tokenizer_config.json
├── transformer
│   ├── config.json
│   ├── diffusion_pytorch_model-00001-of-00003.safetensors
│   ├── diffusion_pytorch_model-00002-of-00003.safetensors
│   ├── diffusion_pytorch_model-00003-of-00003.safetensors
│   └── diffusion_pytorch_model.safetensors.index.json
└── vae
    ├── config.json
    └── diffusion_pytorch_model.safetensors

/root/autodl-tmp/.cache/Dinov2-giant/
.
├── README.md
├── config.json
├── configuration.json
├── model.safetensors
└── preprocessor_config.json

/root/autodl-tmp/.cache/Siglip-so400m-patch14-384/
.
├── README.md
├── config.json
├── model.safetensors
├── preprocessor_config.json
├── special_tokens_map.json
├── spiece.model
├── tokenizer.json
└── tokenizer_config.json
```

---
# ComfyUI-InstantCharacter

ComfyUI-InstantCharacter 

https://github.com/Tencent/InstantCharacter
ComfyUI Warpper

now Need 45GB VRAM, (now open offload will error, fix offload and open it will run on 24GB VRAM.)

flux model & image encoder will autodownload

    flux model donwload to models/unet 

    image encoder download to models/clipvision


ipadapter need download to models/ipadapter

https://huggingface.co/tencent/InstantCharacter/blob/main/instantcharacter_ip-adapter.bin

![show](./assets/show.jpg)


## Online Run:

app run: [Flux Instant Character](https://www.comfyonline.app/explore/app/flux-instant-character)

https://www.comfyonline.app comfyonline is comfyui cloud website, Run ComfyUI workflows online and deploy APIs with one click

Provides an online environment for running your ComfyUI workflows, with the ability to generate APIs for easy AI application development.



## Paper Analysis

**Analysis of the Paper "Instant Character: Personalize Any Characters with a Scalable Diffusion Transformer Framework"**

This paper introduces InstantCharacter, a novel framework that marks significant progress in personalized character image generation, particularly by leveraging powerful Diffusion Transformer (DiT) models like FLUX.1. Its goal is to generate high-quality images of a specific character provided by the user (via a reference image) in various new scenarios, poses, and styles described by text prompts, all while maintaining high character identity consistency and precise adherence to the text instructions.

**Comparative Analysis Against Related Methods:**

The paper qualitatively compares InstantCharacter against other personalization methods also built upon the FLUX foundation, highlighting its advantages:

*   **Vs. OminiControl and EasyControl:** These methods struggle significantly with maintaining **character identity consistency**. The generated characters often show noticeable differences from the reference image, failing to effectively preserve key identity features.
*   **Vs. ACE++:** While slightly better at identity preservation, ACE++ only maintains partial features, particularly in simple scenarios. Its primary weakness lies in **text controllability**, especially when dealing with complex, action-oriented prompts, often resulting in inaccurate or unnatural outputs.
*   **Vs. UNO:** UNO excels at **identity consistency**, but often *over-preserves* it. This comes at the cost of reduced **editability**. It finds it difficult to flexibly alter the character's pose or actions according to the text prompt or to integrate the character naturally into new backgrounds, sometimes resembling a simple "copy-paste" effect.
*   **InstantCharacter's Advantages:** In contrast, InstantCharacter achieves an excellent balance between **identity consistency**, **text controllability** (especially for complex actions and scene integration), and overall **image fidelity**. It reliably "remembers" the character's appearance while flexibly and accurately creating high-quality images based on text instructions, even for complex prompts like "a character riding a bicycle" or "playing the piano in a specific location." Experiments show its performance surpasses the aforementioned open-source methods and is comparable to the powerful, closed-source GPT4o. Furthermore, InstantCharacter demonstrates good compatibility with style LoRAs, enabling stylized character generation easily.

**Key Factors Behind InstantCharacter's Success:**

InstantCharacter's outstanding performance stems from the synergistic combination of several critical elements:

1.  **Scalable Adapter Specifically Designed for DiTs:** Unlike traditional adapters often meant for U-Nets, InstantCharacter employs a full Transformer architecture that is highly compatible with the underlying DiT model (FLUX). This ensures efficient interaction and information flow. Its design is inherently scalable to match future, more powerful DiTs. It effectively injects character features into the DiT's generation process using a timestep-aware Q-former and cross-attention mechanisms.
2.  **Advanced and Robust Character Feature Extraction:**
    *   It utilizes a combination of **SigLIP** (for fine-grained details crucial for identity) and **DINOv2** (for robust features resistant to background noise) instead of relying on a single encoder, providing more comprehensive and reliable character appearance information.
    *   A **multi-level feature fusion** strategy is employed. It processes both low-level features from shallow encoder layers and region-level features obtained via patching, using dedicated intermediate encoders before fusion. This ensures that features across different scales are captured and utilized, minimizing information loss.
3.  **Large-Scale Structured Dataset:** A massive dataset containing 10 million samples of diverse characters was curated. Crucially, it includes both **paired** data (character image + target text description) and **unpaired** data (single character image), providing the foundation for the specialized training strategy.
4.  **Progressive, Decoupled Training Strategy:** An innovative three-stage training approach effectively decouples the sometimes conflicting objectives of **character consistency**, **text controllability**, and **image fidelity** by focusing on them in different phases:
    *   *Stage 1 (Low-res, Unpaired):* Focuses on learning **character consistency**.
    *   *Stage 2 (Low-res, Paired):* Focuses on learning **text controllability**.
    *   *Stage 3 (High-res, Mixed):* Fine-tunes using high-resolution data to enhance **image fidelity** and texture details.
    This strategy is not only effective but also improves training efficiency by handling major learning tasks at lower resolutions.

**Conclusion:**

The success of InstantCharacter is not attributed to a single breakthrough but to the systematic integration of a powerful DiT foundation, a bespoke adapter architecture, intelligent feature extraction techniques, a vast and structured dataset, and a meticulously designed training strategy. This comprehensive approach allows it to set a new benchmark in personalized character generation, particularly in balancing identity preservation, text control, and image quality. It offers significant contributions to the field of controllable image generation, especially for DiT-based applications, and provides valuable insights for adapting foundation models to specialized tasks.




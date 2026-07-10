from .nodes import ComfyUILlamaCppUnloaderExtension

async def comfy_entrypoint() -> ComfyUILlamaCppUnloaderExtension:
    return ComfyUILlamaCppUnloaderExtension()
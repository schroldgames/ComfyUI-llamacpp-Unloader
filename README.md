# ComfyUI-llamacpp-Unloader

Unload llama.cpp models from VRAM to free GPU memory in ComfyUI.

## What it does

Queries a running llama.cpp inference server for currently loaded models and unloads them, freeing their VRAM so other ComfyUI workflows can run without OOM errors.

## Installation

### Via ComfyUI Manager (recommended)

1. Open ComfyUI Manager
2. Search for `ComfyUI-llamacpp-Unloader`
3. Click Install
4. Restart ComfyUI

### Manual installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/schroldgames/ComfyUI-llamacpp-Unloader.git
cd ComfyUI-llamacpp-Unloader
pip install -r requirements.txt
```

## Usage

Wire the node into your workflow. The `llama_api` input defaults to `http://host.docker.internal:8081`, which works for Docker-based llama.cpp deployments on macOS/Windows. Adjust if your server runs at a different address.

### Excluding models

The optional **Exclude Models** text area lets you specify model IDs that should not be unloaded (one per line or comma-separated). Any loaded model whose ID matches an excluded entry will be skipped — all other loaded models are still unloaded.

### Gotcha: execution order

ComfyUI does not guarantee execution order between parallel branches. To ensure the unload fires after your generation workflow completes, insert a **Reroute** node to enforce ordering — wire the last node of your generation chain into the Reroute, then from the Reroute into this node's inputs. This forces ComfyUI to execute the unload only after generation finishes.

## Outputs

- **success** (Boolean) — `true` if the operation completed successfully (including when no models were loaded), `false` on error
- **result** (String) — human-readable status message with per-model results, also shown as inline preview text in the node UI

### Failure mode

If the llama API is unreachable (no llama.cpp server at the given address), the node returns `success: false` with an error message rather than crashing your workflow.

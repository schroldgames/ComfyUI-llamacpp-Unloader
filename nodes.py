import requests
import urllib3
from comfy_api.latest import ComfyExtension, io, ui

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LlamaCppUnloader(io.ComfyNode):
    """Unload llama.cpp models from VRAM."""
    
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ComfyUI-llamacpp-Unloader",
            display_name="Unload llama.cpp Models",
            category="system/VRAM",
            inputs=[
                io.String.Input("llama_api"),
                io.String.Input("exclude_models", multiline=True, default=""),
            ],
            outputs=[
                io.Boolean.Output("success"),
                io.String.Output("result"),
            ],
            is_output_node=True,
        )

    @classmethod
    def fingerprint_inputs(cls, llama_api, exclude_models=""):
        """Force re-execution every run by returning a unique value."""
        import uuid
        return str(uuid.uuid4())

    @classmethod
    async def execute(cls, llama_api, exclude_models="") -> io.NodeOutput:
        DEFAULT_LLAMA_API = "http://host.docker.internal:8081"
        
        exclude_ids = set()
        if exclude_models.strip():
            for line in exclude_models.split("\n"):
                line = line.strip().strip(",")
                if line:
                    exclude_ids.add(line)

        try:
            resp = requests.get(f"{llama_api}", timeout=5, verify=False)

            if resp.status_code != 200:
                msg = f"GET /models failed: {resp.text[:100]}"
                return io.NodeOutput(False, msg, ui=ui.PreviewText(msg))

            data = resp.json()
            loaded = [m for m in data.get("data", [])
                      if m.get("status", {}).get("value") == "loaded"]

        except Exception as e:
            msg = f"GET /models error: {str(e)[:100]}"
            return io.NodeOutput(False, msg, ui=ui.PreviewText(msg))

        if not loaded:
            msg = "No models currently loaded"
            return io.NodeOutput(True, msg, ui=ui.PreviewText(msg))

        results = []
        for model in loaded:
            model_id = model.get("id", "")
            if model_id and any(model_id == eid for eid in exclude_ids):
                continue
            try:
                unld = requests.post(
                    f"{llama_api}/models/unload",
                    json={"model": model_id},
                    timeout=5, verify=False
                )
                payload = unld.json()
                if payload.get("success") is True:
                    results.append(f"'{model_id}' → OK")
                else:
                    results.append(f"'{model_id}' → {unld.text[:80]}")
            except Exception as e:
                results.append(f"'{model_id}' → Error: {str(e)[:60]}")

        result_text = "; ".join(results)
        return io.NodeOutput(True, result_text, ui=ui.PreviewText(result_text))


class ComfyUILlamaCppUnloaderExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [LlamaCppUnloader]


async def comfy_entrypoint() -> ComfyExtension:
    return ComfyUILlamaCppUnloaderExtension()

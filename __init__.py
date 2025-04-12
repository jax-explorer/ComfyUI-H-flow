from .nodes.LoadLoraFromCivitAI import LoadLoraFromCivitAIWithDownloader
from .nodes.LoadLoraFromHF import LoadLoraFromHFWithDownloader, LoadLoraFromHFWithToken
from .nodes.LoadLoraFromComfyOnline import LoadLoraFromComfyOnlineWithDownloader

from .nodes.nodes import LoadHunyuanLoraFromCivitAIWithDownloader, LoadWanVideoLoraFromHFWithDownloader
from .nodes.nodes import LoadHunyuanLoraFromHFWithDownloader
from .nodes.nodes import LoadHunyuanLoraFromComfyOnlineWithDownloader
from .nodes.nodes import LoadWanVideoLoraFromComfyOnlineWithDownloader

from .nodes.upload_anything import UploadAnything
from .nodes.save_file import ComfyOnlineSaveFile
from .nodes.LoadEmbedding import EmbeddingLoader
from .nodes.AudioSave import SaveAudioAsWav
from .nodes.TextSave import TextSave
from .nodes.nodes import LoadWanVideoLoraFromCivitAIWithDownloader
from .nodes.LoadCheckpointFromCivitAI import LoadCheckpointFromCivitAIWithDownloader
NODE_CLASS_MAPPINGS = { 
    "LoadLoraFromCivitAI":LoadLoraFromCivitAIWithDownloader,
    "LoadLoraFromComfyOnline":LoadLoraFromComfyOnlineWithDownloader,
    "LoadHunyuanLoraFromCivitAI":LoadHunyuanLoraFromCivitAIWithDownloader,
    "LoadHunyuanLoraFromComfyOnline":LoadHunyuanLoraFromComfyOnlineWithDownloader,
    "LoadWanVideoLoraFromComfyOnline":LoadWanVideoLoraFromComfyOnlineWithDownloader,
    "LoadWanVideoLoraFromCivitAI":LoadWanVideoLoraFromCivitAIWithDownloader,
    "LoadWanVideoLoraFromHF": LoadWanVideoLoraFromHFWithDownloader,
    "LoadHunyuanLoraFromHF":LoadHunyuanLoraFromHFWithDownloader,
    "LoadLoraFromHF":LoadLoraFromHFWithDownloader,
    "LoadLoraFromHFWithToken": LoadLoraFromHFWithToken,
    "ComfyOnlineUploadAnything": UploadAnything,
    "ComfyOnlineSaveFile": ComfyOnlineSaveFile,
    "EmbeddingLoader": EmbeddingLoader,
    "SaveAudioAsWav": SaveAudioAsWav,
    "SaveText": TextSave,
    "LoadCheckpointFromCivitAI": LoadCheckpointFromCivitAIWithDownloader,

}
NODE_DISPLAY_NAME_MAPPINGS = { 
    "LoadLoraFromCivitAI" : "Load Lora From CivitAI",
    "LoadLoraFromComfyOnline": "Load Lora From ComfyOnline",
    "LoadLoraFromHF" : "Load Lora From HuggingFace",
    "LoadLoraFromHFWithToken": "Load Lora From HuggingFace (with Token)",
    "LoadHunyuanLoraFromComfyOnline":" Load Lora From ComfyOnline",
    "LoadHunyuanLoraFromCivitAI": "Load HunyuanLora From CivitAI",
    "LoadHunyuanLoraFromHF": "Load HunyuanLora From HF",
    "LoadWanVideoLoraFromCivitAI": "Load WanVideoLora From CivitAI",
    'ComfyOnlineUploadAnything': "ComfyOnlineUploadAnything",
    "ComfyOnlineSaveFile": "ComfyOnlineSaveFile",
    "EmbeddingLoader": "Load Embedding",
    "SaveAudioAsWav": "Save Audio As Wav",
    "SaveText": "Save Text ComfyOnline",
    "LoadCheckpointFromCivitAI": "Load Checkpoint From CivitAI",
    "LoadWanVideoLoraFromComfyOnline": "Load WanVideoLora From ComfyOnline",
    "LoadWanVideoLoraFromHF": "Load WanVideoLora From HF",
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', "WEB_DIRECTORY"]
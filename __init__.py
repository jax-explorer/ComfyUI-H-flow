from nodes.FluxPro import FluxProUltra
from nodes.IdeogramV2 import IdeogramV2Turbo
from nodes.Kling import KlingImageToVideo
from nodes.LLM import LLMTask
from nodes.Runway import RunwayImageToVideo
from nodes.SaveImage import SaveImage
from nodes.SaveVideo import SaveVideo
from nodes.wan2 import Wan2ImageToVideo


NODE_CLASS_MAPPINGS = {
  "Wan2ImageToVideo": Wan2ImageToVideo,
      "LLMTask": LLMTask,
      "SaveImage": SaveImage,
      "SaveVideo": SaveVideo,
      "FluxProUltra": FluxProUltra,
      "IdeogramV2Turbo": IdeogramV2Turbo,
      "RunwayImageToVideo": RunwayImageToVideo,
      "KlingImageToVideo": KlingImageToVideo,

}

NODE_DISPLAY_NAME_MAPPINGS = {
  "Wan2ImageToVideo": "Wan2-1 Image To Video",
  "LLMTask": "LLM Task",
  "SaveImage": "Save Image",
  "SaveVideo": "Save Video",
  "ShowText": "Show Text",
  "FluxProUltra": "FluxPro Ultra",
  "IdeogramV2Turbo": "IdeogramV2 Turbo",
  "RunwayImageToVideo": "Runway Image To Video",
  "KlingImageToVideo": "Kling Image To Video",
  "ReplaceText": "Replace Text",
  "JoinText": "Join Text",
  "TestImage": "Test Image",
  "TestText": "Test Text"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', "WEB_DIRECTORY"]
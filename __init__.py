from .nodes.FluxPro import FluxProUltra
from .nodes.IdeogramV2 import IdeogramV2Turbo
from .nodes.Kling import KlingImageToVideo
from .nodes.LLM import LLMTask
from .nodes.Runway import RunwayGen3ImageToVideo
from .nodes.SaveImage import SaveImage
from .nodes.SaveVideo import SaveVideo
from .nodes.wan2 import Wan2ImageToVideo
from .nodes.HiDreamI1 import HiDreamI1
from .nodes.LoadImage import LoadImage
from .nodes.Luma import LumaRay2ImageToVideo
from .nodes.Hailuo import Hailuo01ImageToVideo

NODE_CLASS_MAPPINGS = {
    "Wan2ImageToVideo": Wan2ImageToVideo,
    "LLMTask": LLMTask,
    "FluxProUltra": FluxProUltra,
    "IdeogramV2Turbo": IdeogramV2Turbo,
    "RunwayGen3ImageToVideo": RunwayGen3ImageToVideo,
    "KlingImageToVideo": KlingImageToVideo,
    "HiDreamI1": HiDreamI1,
    "HFLowLoadImage": LoadImage,
    "LumaRay2ImageToVideo": LumaRay2ImageToVideo,
    "Hailuo01ImageToVideo": Hailuo01ImageToVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "Wan2ImageToVideo": "Wan2-1 Image To Video",
  "LLMTask": "LLM Task",
  "FluxProUltra": "FluxPro Ultra",
  "IdeogramV2Turbo": "IdeogramV2 Turbo",
  "RunwayGen3ImageToVideo": "Runway Gen3 Image To Video",
  "KlingImageToVideo": "Kling Image To Video",
  "HiDreamI1": "HiDream I1",
  "HFLowLoadImage": "HFLow Load Image",
  "LumaRay2ImageToVideo": "Luma Ray2 Image To Video",
  "Hailuo01ImageToVideo": "Hailuo01 Image To Video"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', "WEB_DIRECTORY"]
import os
import json
import time
import requests
from server import PromptServer
from aiohttp import web
import nodes
import folder_paths
import random
from .utils import get_comfyonline_api_key

class FluxProUltra:

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.prefix_append = ""
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "1:1" }),
                "raw": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_url",)
    FUNCTION = "generate_image"
    CATEGORY = "H-flow.Image"
    OUTPUT_NODE = True


    def generate_image(self, prompt, seed, aspect_ratio, raw):
        # 使用默认值
        max_wait_time = 3600  # 默认等待时间为3600秒
        polling_interval = 10  # 默认轮询间隔为10秒
        results = list()

        # 从环境变量获取API令牌
        api_token = get_comfyonline_api_key()
        if not api_token:
            return ("Error: No API token provided. Please set FLUX_PRO_API_TOKEN environment variable.",)
        
        # 创建任务
        create_task_url = "https://api.comfyonline.app/api/un-api/create_flux_pro_ultra_task"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }
        
        payload = {
            "prompt": prompt,
            "seed": seed,
            "aspect_radio": aspect_ratio,
            "raw": raw
        }
    
        
        try:
            response = requests.post(create_task_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data') or not data['data'].get('task_id'):
                raise Exception(f"Failed to create task: {json.dumps(data)}")
            
            task_id = data['data']['task_id']
            print(f"FluxPro task created with ID: {task_id}")
            filename_prefix = "FluxPro"

            # 轮询查询任务状态
            query_url = "https://api.comfyonline.app/api/query_app_general_detail"
            start_time = time.time()
            full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, 0, 0)
            
            while time.time() - start_time < max_wait_time:
                query_payload = {"task_id": task_id}
                query_response = requests.post(query_url, headers=headers, json=query_payload)
                query_response.raise_for_status()
                query_data = query_response.json()
                query_data = query_data['data']
                status = query_data.get('status')
                print(f"FluxPro task status: {status}")
                
                if status == "COMPLETED":
                    output = query_data.get('output', {})
                    output_url_list = output.get('output_url_list', [])
                    
                    if output_url_list and len(output_url_list) > 0:

                        counter = random.randint(1, 100000)
                        file = f"{filename_prefix}_{counter:05}_.png"

                        output_path = os.path.join(full_output_folder, file)
                        
                        # Download the image directly to disk with minimal memory usage
                        response = requests.get(output_url_list[0], stream=True, timeout=10)
                        response.raise_for_status()
                        
                        # Save the downloaded image directly to disk
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)

                            results.append({
                                "filename": file,
                                "subfolder": subfolder,
                                "type": self.type,
                                "url": output_url_list[0]
                            })
                            print(results)
                        return {"ui": {"images": results}, "result": (output_url_list[0],)}
                    else:
                        raise Exception("Task completed but no output URL found")
                
                elif status == "FAILED":
                    error_message = query_data.get('error_message', 'Unknown error')
                    raise Exception(f"Task failed: {error_message}")
                
                # 如果任务仍在进行中，等待一段时间后再次查询
                time.sleep(polling_interval)

            
            # 如果超过最大等待时间，抛出异常
            raise Exception(f"Task timed out after {max_wait_time} seconds")
            
        except Exception as e:
            print(f"Error in FluxProUltra: {str(e)}")
            return (f"Error: {str(e)}",)

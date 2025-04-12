import os
import json
import time
import requests
from nodes.utils import get_comfyonline_api_key
from server import PromptServer
from aiohttp import web
import nodes
import folder_paths
import random

class KlingImageToVideo:

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
                "image_url": ("STRING", {"default": ""}),
                "aspect_ratio": ("STRING", {"default": "16:9", "choices": ["1:1", "4:3", "16:9", "9:16"]}),
                "duration": ("INT", {"default": 4, "min": 1, "max": 16}),
                "is_pro": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "image_to_video"
    CATEGORY = "Video"
    OUTPUT_NODE = True

    def image_to_video(self, prompt, image_url, aspect_ratio, duration, is_pro, webhook=""):
        # 使用默认值
        max_wait_time = 3600  # 默认等待时间为3600秒
        polling_interval = 10  # 默认轮询间隔为10秒
        
        results = list()
        filename_prefix = "KlingVideo"

        api_token = get_comfyonline_api_key()
        if not api_token:
            return ("Error: No API token provided. Please set COMFYONLINE_TOKEN environment variable.",)
        
        # 创建任务
        create_task_url = "https://api.comfyonline.app/api/un-api/create_kling_image2video_task"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "aspect_radio": aspect_ratio,
            "duration": duration,
            "isPro": is_pro
        }
        
        try:
            response = requests.post(create_task_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data') or not data['data'].get('task_id'):
                raise Exception(f"Failed to create task: {json.dumps(data)}")
            
            task_id = data['data']['task_id']
            print(f"Task created with ID: {task_id}")
            
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
                print(query_data)
                status = query_data.get('status')
                print(f"Task status: {status}")
                
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
                        return {"ui": {"videos": results}, "result": (output_url_list[0],)}
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
            print(f"Error in KlingImageToVideo: {str(e)}")
            return (f"Error: {str(e)}",)

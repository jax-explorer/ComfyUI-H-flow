import os
import json
import time
import requests

from .utils import get_comfyonline_api_key, process_image_path_or_url

class RunwayGen3ImageToVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "image_url": ("STRING", {"default": ""}),
                "aspect_ratio": (["1:1", "16:9", "9:16"], {"default": "16:9"}),
                "duration": ([5, 10], {"default": 5}),
            },
            "optional": {
                "webhook": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "image_to_video"
    CATEGORY = "Video"

    def image_to_video(self, prompt, image_url, aspect_ratio, duration, webhook=""):
        # 使用默认值
        max_wait_time = 3600  # 默认等待时间为3600秒
        polling_interval = 10  # 默认轮询间隔为10秒
        
        # 从环境变量获取API令牌
        api_token = get_comfyonline_api_key()
        if not api_token:
            return ("Error: No API token provided. Please set COMFYONLINE_TOKEN environment variable.",)
        
        # 创建任务
        create_task_url = "https://api.comfyonline.app/api/un-api/create_runway_image2video_task"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'
        }
        image_url = process_image_path_or_url(image_url)
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "aspect_radio": aspect_ratio,
            "duration": duration
        }
        
        # 如果提供了webhook，则添加到payload中
        if webhook:
            payload["webhook"] = webhook
        
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
            
            while time.time() - start_time < max_wait_time:
                query_payload = {"task_id": task_id}
                query_response = requests.post(query_url, headers=headers, json=query_payload)
                query_response.raise_for_status()
                query_data = query_response.json()
                
                status = query_data.get('status')
                print(f"Task status: {status}")
                
                if status == "COMPLETED":
                    output = query_data.get('output', {})
                    output_url_list = output.get('output_url_list', [])
                    
                    if output_url_list and len(output_url_list) > 0:
                        return (output_url_list[0],)
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
            print(f"Error in RunwayImageToVideo: {str(e)}")
            return (f"Error: {str(e)}",)

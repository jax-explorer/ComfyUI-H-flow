import json
import time
import requests
import os
import folder_paths
from .utils import get_comfyonline_api_key

class LLMTask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (["deepseek-r1", "gpt-4o", "gpt-4o-mini", 
                          "claude-3-7-sonnet", "claude-3-5-sonnet", 
                          "gemini-2.0-flash"],{"default": "gpt-4o" }),
                "prompt": ("STRING", {"multiline": True}),

            },
            "optional": {
                "context": ("STRING", {"default": '', "forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("content",)
    FUNCTION = "execute"
    CATEGORY = "LLM"
    OUTPUT_NODE = True

    def execute(self, model, prompt, context=""):
        # 创建 LLM 任务
        if context:
            prompt = prompt + "\n" + "context:" + context
        task_id = self.create_llm_task(prompt, model)
        print(f"task_id {task_id}")
        if not task_id:
            return ("Failed to create LLM task",)
        
        # 轮询任务状态
        content = self.poll_task_status(task_id)
        return {"ui": {"text": content}, "result": content}
    
    def create_llm_task(self, prompt, model, context=""):
        url = "https://api.comfyonline.app/api/un-api/create_LLM_task"
        
    
        if model == "gpt-4o-mini":
            model = "OpenAI-gpt-4o-mini"
        
        if model == "gpt-4o":
            model = "OpenAI-gpt-4o"
        
        if model == "deepseek-r1":
            model = "Deepseek-deepseek-reasoner"
        
        if model == "gemini-2.0-flash":
            model = "Gemini-gemini-2.0-flash"
        
        if model == "claude-3-7-sonnet":
            model = "Claude-claude-3-7-sonnet-20250219"
            
        if model == "claude-3-5-sonnet":
            model = "Claude-claude-3-5-sonnet-20241022"
            
        
        
        
        
        # 构建请求体
        body = {
            "prompt": prompt,
            "model": model,
            "webhook": "",  # 不使用 webhook，我们将通过轮询获取结果
        }
        
        print("start create llm task")
        # 如果提供了上下文，则添加到请求体中
        if context:
            body["context"] = context
        
        api_token = get_comfyonline_api_key()
        if not api_token:
            return ("Error: No API token provided. Please set COMFYONLINE_TOKEN environment variable.",)
        
        print(f"api_token {api_token}")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'  # 空令牌，实际应用中可能需要配置
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data and 'task_id' in data['data']:
                return data['data']['task_id']
            else:
                print(f"Error creating LLM task: {data}")
                return None
        except Exception as e:
            print(f"Exception when creating LLM task: {e}")
            return None
    
    def poll_task_status(self, task_id):
        url = "https://api.comfyonline.app/api/query_app_general_detail"
        api_token = get_comfyonline_api_key()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}'  # 空令牌，实际应用中可能需要配置
        }
        body = {
            "task_id": task_id
        }
        
        # 固定参数：5秒间隔，最大360秒
        poll_interval = 5
        max_poll_time = 360
        
        start_time = time.time()
        while time.time() - start_time < max_poll_time:
            try:
                response = requests.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                print(f"data {data}")
                if 'data' in data and 'status' in data['data']:
                    if data['data']['status'] == 'COMPLETED':
                        if 'llm_output' in data['data'] and 'choices' in data['data']['llm_output'] and len(data['data']['llm_output']['choices']) > 0:
                            message = data['data']['llm_output']['choices'][0]['message']
                            if 'content' in message:
                                return (message['content'],)
                            else:
                                return "LLM task completed but no content found in response"
                        else:
                            return "LLM task completed but response format is unexpected"
                    elif data['data']['status'] == 'FAILED':
                        error_message = data['data'].get('error_message', 'Unknown error')
                        return f"LLM task failed: {error_message}"
                    # 如果状态是 IN_PROGRESS，继续轮询
                
                # 等待指定的轮询间隔
                time.sleep(poll_interval)
            except Exception as e:
                print(f"Exception when polling task status: {e}")
                time.sleep(poll_interval)
        
        return "LLM task timed out after waiting for maximum poll time"

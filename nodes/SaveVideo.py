import os
import json
import folder_paths
import requests
from io import BytesIO

class SaveVideo:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_urls": ("STRING", {"default": "", "multiline": True, "tooltip": "The URLs of videos to download and save. One URL per line."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd%."})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_videos"

    OUTPUT_NODE = True

    CATEGORY = "video"
    DESCRIPTION = "Downloads videos from URLs and saves them to your ComfyUI output directory."

    def save_videos(self, video_urls, filename_prefix="ComfyUI"):
        filename_prefix += self.prefix_append
        
        # Split the input by newlines to handle multiple URLs
        urls = [url.strip() for url in video_urls.split('\n') if url.strip()]
        
        if not urls:
            print("No valid video URLs provided")
            return {"ui": {"videos": []}}
        
        results = list()
        counter = 1
        
        # Get the save path
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, 0, 0)
        
        for (batch_number, url) in enumerate(urls):
            try:
                # Create filename
                filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
                file = f"{filename_with_batch_num}_{counter:05}_.mp4"
                output_path = os.path.join(full_output_folder, file)
                
                # Download the video directly to disk with minimal memory usage
                response = requests.get(url, stream=True, timeout=30)  # Increased timeout for videos
                response.raise_for_status()
                
                # Save the downloaded video directly to disk
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type,
                    "url": url
                })
                counter += 1
                
                print(f"Successfully downloaded and saved video from {url} to {output_path}")
                
            except Exception as e:
                print(f"Error downloading or saving video from URL {url}: {str(e)}")
                continue
        
        return {"ui": {"videos": results}}
import os
import json
import folder_paths
import requests

class SaveImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_urls": ("STRING", {"default": "", "multiline": True, "tooltip": "The URLs of images to download and save. One URL per line."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd%."})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "image"
    DESCRIPTION = "Downloads images from URLs and saves them to your ComfyUI output directory."

    def save_images(self, image_urls, filename_prefix="ComfyUI"):
        filename_prefix += self.prefix_append
        
        # Split the input by newlines to handle multiple URLs
        urls = [url.strip() for url in image_urls.split('\n') if url.strip()]
        
        if not urls:
            print("No valid image URLs provided")
            return {"ui": {"images": []}}
        
        results = list()
        counter = 1
        
        # We don't know image dimensions yet, so we'll pass 0, 0 and let the function handle it
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, 0, 0)
        
        for (batch_number, url) in enumerate(urls):
            try:
                # Create filename
                filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
                file = f"{filename_with_batch_num}_{counter:05}_.png"
                output_path = os.path.join(full_output_folder, file)
                
                # Download the image directly to disk with minimal memory usage
                response = requests.get(url, stream=True, timeout=10)
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
                    "url": url
                })
                counter += 1
                
                print(f"Successfully downloaded and saved image from {url} to {output_path}")
                
            except Exception as e:
                print(f"Error downloading or saving image from URL {url}: {str(e)}")
                continue
        
        return {"ui": {"images": results}}
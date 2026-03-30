import os

class JSGDeleteFilePassImage:
    DESCRIPTION = "Deletes a file from disk in a passthrough workflow."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = ("Returns the original image input unchanged.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("IMAGE", {"tooltip": "The image value to pass through unchanged."}),
                "file_path": ("STRING", {"multiline": False, "tooltip": "The file path to delete."}),
                "delete_enabled": ("BOOLEAN", {"default": False, "tooltip": "Whether to delete the file."}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough, delete_enabled):
        path = (file_path or "").strip().strip('"').strip("'")
        if delete_enabled and os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[JSGDeleteFile] File '{path}' deleted!")
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)
    
class JSGDeleteFilePassAny:
    DESCRIPTION = "Deletes a file from disk in a passthrough workflow."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = ("Returns the original input value unchanged.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("*", {"tooltip": "The input value to pass through unchanged."}),
                "file_path": ("STRING", {"multiline": False, "tooltip": "The file path to delete."}),
                "delete_enabled": ("BOOLEAN", {"default": False, "tooltip": "Whether to delete the file."}),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough, delete_enabled):
        path = (file_path or "").strip().strip('"').strip("'")
        if delete_enabled and os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[JSGDeleteFile] File '{path}' deleted!")
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)
    
class JSGDeleteFilePassString:
    DESCRIPTION = "Deletes a file from disk in a passthrough workflow."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = ("Returns the original string input unchanged.",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("STRING", {"tooltip": "The string value to pass through unchanged."}),
                "file_path": ("STRING", {"multiline": False, "tooltip": "The file path to delete."}),
                "delete_enabled": ("BOOLEAN", {"default": False, "tooltip": "Whether to delete the file."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough, delete_enabled):
        path = (file_path or "").strip().strip('"').strip("'")
        if delete_enabled and os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[JSGDeleteFile] File '{path}' deleted!")
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)

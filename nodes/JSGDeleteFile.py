import os

class JSGDeleteFilePassImage:
    DESCRIPTION = "Delete a file from disk and passthrough the input."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("IMAGE", {}),
                "file_path": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough):
        path = (file_path or "").strip().strip('"').strip("'")
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)
    
class JSGDeleteFilePassAny:
    DESCRIPTION = "Delete a file from disk and passthrough the input."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("*", {}),
                "file_path": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough):
        path = (file_path or "").strip().strip('"').strip("'")
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)
    
class JSGDeleteFilePassString:
    DESCRIPTION = "Delete a file from disk and passthrough the input."
    CATEGORY = "JSG Utils/File"
    IS_CHANGED = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "passthrough": ("STRING", {}),
                "file_path": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "delete_file"

    def delete_file(self, file_path, passthrough):
        path = (file_path or "").strip().strip('"').strip("'")
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"[JSGDeleteFile] Could not delete file '{path}': {e}")

        return (passthrough,)

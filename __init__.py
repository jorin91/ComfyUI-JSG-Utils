from .nodes.JSGFindImagesRecursiveList import JSGFindImagesRecursiveList
from .nodes.JSGParsePath import JSGParsePath
from .nodes.JSGFindImagePathsRecursive import JSGFindImagePathsRecursive
from .nodes.JSGLoadImageFromPath import JSGLoadImageFromPath

NODE_CLASS_MAPPINGS = {
    "JSGFindImagesRecursiveList": JSGFindImagesRecursiveList,
    "JSGParsePath": JSGParsePath,
    "JSGFindImagePathsRecursive": JSGFindImagePathsRecursive,
    "JSGLoadImageFromPath": JSGLoadImageFromPath
}

#  =================================================================================
NODE_DISPLAY_NAME_MAPPINGS = {
    "JSGFindImagesRecursiveList": "Find Images Recursively (List)",
    "JSGParsePath": "Parse Filesystem Path",
    "JSGFindImagePathsRecursive": "Find Image Paths (Recursive)",
    "JSGLoadImageFromPath": "Load Image From Path"
}

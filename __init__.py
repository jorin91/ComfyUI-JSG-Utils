from .nodes.JSGFindImagesRecursiveList import JSGFindImagesRecursiveList
from .nodes.JSGParsePath import JSGParsePath
from .nodes.JSGFindImagePathsRecursive import JSGFindImagePathsRecursive
from .nodes.JSGLoadImageFromPath import JSGLoadImageFromPath
from .nodes.JSGDeleteFile import JSGDeleteFilePassImage, JSGDeleteFilePassAny, JSGDeleteFilePassString
from .nodes.JSGRandomColor import JSGRandomColorHSV

NODE_CLASS_MAPPINGS = {
    "JSGFindImagesRecursiveList": JSGFindImagesRecursiveList,
    "JSGParsePath": JSGParsePath,
    "JSGFindImagePathsRecursive": JSGFindImagePathsRecursive,
    "JSGLoadImageFromPath": JSGLoadImageFromPath,
    "JSGDeleteFilePassImage": JSGDeleteFilePassImage,
    "JSGDeleteFilePassAny": JSGDeleteFilePassAny,
    "JSGDeleteFilePassString": JSGDeleteFilePassString,
    "JSGRandomColorHSV": JSGRandomColorHSV
}

#  =================================================================================
NODE_DISPLAY_NAME_MAPPINGS = {
    "JSGFindImagesRecursiveList": "Find Images Recursively (List)",
    "JSGParsePath": "Parse Filesystem Path",
    "JSGFindImagePathsRecursive": "Find Image Paths (Recursive)",
    "JSGLoadImageFromPath": "Load Image From Path",
    "JSGDeleteFilePassImage": "Delete File (Image Passthrough)",
    "JSGDeleteFilePassAny": "Delete File (* Passthrough)",
    "JSGDeleteFilePassString": "Delete File (String Passthrough)",
    "JSGRandomColorHSV": "Random Color (HSV)"
}

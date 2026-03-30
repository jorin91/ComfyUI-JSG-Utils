from .nodes.JSGFindImagesRecursiveList import JSGFindImagesRecursiveList
from .nodes.JSGParsePath import JSGParsePath
from .nodes.JSGFindImagePathsRecursive import JSGFindImagePathsRecursive
from .nodes.JSGLoadImageFromPath import JSGLoadImageFromPath
from .nodes.JSGDeleteFile import JSGDeleteFilePassImage, JSGDeleteFilePassAny, JSGDeleteFilePassString
from .nodes.JSGRandomColor import JSGRandomColorHSVA
from .nodes.JSGSaveImage import JSGSaveImage
from .nodes.JSGSetMetadata import JSGSetMetadata
from .nodes.JSGAddMetadata import JSGAddMetadata
from .nodes.JSGRemoveMetadata import JSGRemoveMetadata
from .nodes.JSGCaptionBuilder import JSGCaptionBuilder
from .nodes.JSGRandomStringChoice import JSGRandomStringChoice
from .nodes.JSGCombineStrings import JSGCombineStrings
from .nodes.JSGBoolToString import JSGBoolToString

WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "JSGFindImagesRecursiveList": JSGFindImagesRecursiveList,
    "JSGParsePath": JSGParsePath,
    "JSGFindImagePathsRecursive": JSGFindImagePathsRecursive,
    "JSGLoadImageFromPath": JSGLoadImageFromPath,
    "JSGDeleteFilePassImage": JSGDeleteFilePassImage,
    "JSGDeleteFilePassAny": JSGDeleteFilePassAny,
    "JSGDeleteFilePassString": JSGDeleteFilePassString,
    "JSGRandomColorHSVA": JSGRandomColorHSVA,
    "JSGSaveImage": JSGSaveImage,
    "JSGSetMetadata": JSGSetMetadata,
    "JSGAddMetadata": JSGAddMetadata,
    "JSGRemoveMetadata": JSGRemoveMetadata,
    "JSGCaptionBuilder": JSGCaptionBuilder,
    "JSGRandomStringChoice": JSGRandomStringChoice,
    "JSGCombineStrings": JSGCombineStrings,
    "JSGBoolToString": JSGBoolToString,
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
    "JSGRandomColorHSVA": "Random Color (HSVA)",
    "JSGSaveImage": "Save Image",
    "JSGSetMetadata": "Set Metadata",
    "JSGAddMetadata": "Add Metadata",
    "JSGRemoveMetadata": "Remove Metadata",
    "JSGCaptionBuilder": "Caption Builder (Key + Tags + Description)",
    "JSGRandomStringChoice": "Random String Choice",
    "JSGCombineStrings": "Combine Strings",
    "JSGBoolToString": "Bool To String",
}

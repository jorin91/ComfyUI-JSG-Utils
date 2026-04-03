from .nodes.JSGFindImagesRecursiveList import JSGFindImagesRecursiveList
from .nodes.JSGParsePath import JSGParsePath
from .nodes.JSGFindImagePathsRecursive import JSGFindImagePathsRecursive
from .nodes.JSGLoadImageFromPath import JSGLoadImageFromPath
from .nodes.JSGDeleteFile import JSGDeleteFilePassImage, JSGDeleteFilePassAny, JSGDeleteFilePassString
from .nodes.JSGRandomColor import JSGRandomColorHSVA
from .nodes.JSGSaveImage import JSGSaveImage
from .nodes.JSGCreateBlankMetadata import JSGCreateBlankMetadata
from .nodes.JSGSetMetadataField import JSGSetMetadataField
from .nodes.JSGSetMetadataFields import JSGSetMetadataFields
from .nodes.JSGSetStandardMetadataField import JSGSetStandardMetadataField
from .nodes.JSGRemoveMetadata import JSGRemoveMetadata
from .nodes.JSGCaptionBuilder import JSGCaptionBuilder
from .nodes.JSGRandomStringChoice import JSGRandomStringChoice
from .nodes.JSGRandomStringChoiceList import JSGRandomStringChoiceList
from .nodes.JSGCombineStrings import JSGCombineStrings
from .nodes.JSGBoolToString import JSGBoolToString
from .nodes.JSGMatchStringList import JSGMatchStringList
from .nodes.JSGRandomBool import JSGRandomBool
from .nodes.JSGBoolSwitch import JSGBoolSwitch
from .nodes.JSGRandomPromptBuilder import JSGRandomPromptBuilder
from .nodes.JSGObjectBuilder import JSGObjectBuilder
from .nodes.JSGObjectUnpack import JSGObjectUnpack
from .nodes.JSGIteratorInputs import JSGIteratorInputs
from .nodes.JSGIteratorList import JSGIteratorList
from .nodes.JSGFormattedStringViewer import JSGFormattedStringViewer

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
    "JSGCreateBlankMetadata": JSGCreateBlankMetadata,
    "JSGSetMetadataField": JSGSetMetadataField,
    "JSGSetMetadataFields": JSGSetMetadataFields,
    "JSGSetStandardMetadataField": JSGSetStandardMetadataField,
    "JSGRemoveMetadata": JSGRemoveMetadata,
    "JSGCaptionBuilder": JSGCaptionBuilder,
    "JSGRandomStringChoice": JSGRandomStringChoice,
    "JSGRandomStringChoiceList": JSGRandomStringChoiceList,
    "JSGCombineStrings": JSGCombineStrings,
    "JSGBoolToString": JSGBoolToString,
    "JSGMatchStringList": JSGMatchStringList,
    "JSGRandomBool": JSGRandomBool,
    "JSGBoolSwitch": JSGBoolSwitch,
    "JSGRandomPromptBuilder": JSGRandomPromptBuilder,
    "JSGObjectBuilder": JSGObjectBuilder,
    "JSGObjectUnpack": JSGObjectUnpack,
    "JSGIteratorInputs": JSGIteratorInputs,
    "JSGIteratorList": JSGIteratorList,
    "JSGFormattedStringViewer": JSGFormattedStringViewer,
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
    "JSGCreateBlankMetadata": "Create Blank Metadata",
    "JSGSetMetadataField": "Set Metadata Field",
    "JSGSetMetadataFields": "Set Metadata Fields",
    "JSGSetStandardMetadataField": "Set Standard Metadata Field",
    "JSGRemoveMetadata": "Remove Metadata",
    "JSGCaptionBuilder": "Caption Builder (Key + Tags + Description)",
    "JSGRandomStringChoice": "Random String Choice",
    "JSGRandomStringChoiceList": "Random String Choice (Comma List)",
    "JSGCombineStrings": "Combine Strings",
    "JSGBoolToString": "Bool To String",
    "JSGMatchStringList": "Match String List",
    "JSGRandomBool": "Random Bool",
    "JSGBoolSwitch": "Bool Switch",
    "JSGRandomPromptBuilder": "Random Prompt Builder",
    "JSGObjectBuilder": "Object Builder",
    "JSGObjectUnpack": "Object Unpack",
    "JSGIteratorInputs": "Iterator (Inputs)",
    "JSGIteratorList": "Iterator (List)",
    "JSGFormattedStringViewer": "Formatted String Viewer",
}

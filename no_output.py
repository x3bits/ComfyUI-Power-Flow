from nodes import SaveImage, PreviewImage


class SaveImageNoOutput(SaveImage):
    OUTPUT_NODE = False
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "Power Flow/Utilities"

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        result = super().save_images(images, filename_prefix, prompt, extra_pnginfo)
        result["result"] = (images,)
        return result


class PreviewImageNoOutput(PreviewImage):
    OUTPUT_NODE = False
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "Power Flow/Utilities"

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        result = super().save_images(images, filename_prefix, prompt, extra_pnginfo)
        result["result"] = (images,)
        return result

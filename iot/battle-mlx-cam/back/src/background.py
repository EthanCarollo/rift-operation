"""Background removal using macOS Vision (default) or rembg (fallback)."""

import time

def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Remove background.
    Priority:
    1. macOS Vision (Fast, native, no download)
    2. rembg (Slower, requires model download)
    
    Returns:
        Tuple of (image_with_transparent_bg, elapsed_time)
    """
    start = time.time()
    
    # Method 1: macOS Vision
    try:
        from AppKit import NSBitmapImageRep, NSPNGFileType
        from Quartz import (
            CGImageSourceCreateWithData, CGImageSourceCreateImageAtIndex,
            CIImage, CIContext, CIFilter, CIColor
        )
        from CoreFoundation import CFDataCreate, kCFAllocatorDefault
        import Vision
        
        # Load image
        cf_data = CFDataCreate(kCFAllocatorDefault, image_bytes, len(image_bytes))
        image_source = CGImageSourceCreateWithData(cf_data, None)
        
        if not image_source:
             raise Exception("Vision: Failed to create image source")
        
        cg_image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
        if not cg_image:
            raise Exception("Vision: Failed to create CGImage")
        
        # Create segmentation request
        request = Vision.VNGenerateForegroundInstanceMaskRequest.alloc().init()
        handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
        
        success, error = handler.performRequests_error_([request], None)
        if not success:
            raise Exception(f"Vision request failed: {error}")
        
        results = request.results()
        if not results or len(results) == 0:
            # No subject? Return original
            return image_bytes, time.time() - start
        
        # Generate mask
        observation = results[0]
        mask_buffer, error = observation.generateScaledMaskForImageForInstances_fromRequestHandler_error_(
            observation.allInstances(), handler, None
        )
        
        if error:
            raise Exception(f"Vision mask generation failed: {error}")
        
        # Apply mask
        mask_ci = CIImage.imageWithCVPixelBuffer_(mask_buffer)
        original_ci = CIImage.imageWithCGImage_(cg_image)
        extent = original_ci.extent()
        
        context = CIContext.context()
        blend_filter = CIFilter.filterWithName_("CIBlendWithMask")
        blend_filter.setValue_forKey_(original_ci, "inputImage")
        
        transparent = CIImage.imageWithColor_(CIColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0))
        blend_filter.setValue_forKey_(transparent, "inputBackgroundImage")
        blend_filter.setValue_forKey_(mask_ci, "inputMaskImage")
        
        output_ci = blend_filter.valueForKey_("outputImage")
        output_cg = context.createCGImage_fromRect_(output_ci, extent)
        
        bitmap_rep = NSBitmapImageRep.alloc().initWithCGImage_(output_cg)
        png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)
        
        return bytes(png_data), time.time() - start

    except Exception as e:
        # print(f"⚠️ Vision failed, trying rembg: {e}")
        pass

    # Method 2: rembg (Fallback)
    try:
        from rembg import remove
        output = remove(image_bytes)
        return output, time.time() - start
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ rembg failed: {e}")
        
    return image_bytes, time.time() - start

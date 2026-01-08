"""Background removal using rembg (u2net) or macOS Vision."""

import time

def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Remove background using rembg (best quality) or fallback to Vision.
    
    Returns:
        Tuple of (image_with_transparent_bg, elapsed_time)
    """
    start = time.time()
    
    # Method 1: Try rembg (Robost, high quality for all objects)
    try:
        from rembg import remove
        output = remove(image_bytes)
        return output, time.time() - start
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ rembg failed: {e}")

    # Method 2: Fallback to macOS Vision (Fast, native, but picky)
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
             print("⚠️ Vision: Failed to create image source")
             return image_bytes, time.time() - start
        
        cg_image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
        if not cg_image:
            print("⚠️ Vision: Failed to create CGImage")
            return image_bytes, time.time() - start
        
        # Create segmentation request
        request = Vision.VNGenerateForegroundInstanceMaskRequest.alloc().init()
        handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
        
        success, error = handler.performRequests_error_([request], None)
        if not success:
            print(f"⚠️ Vision: Request failed - {error}")
            return image_bytes, time.time() - start
        
        results = request.results()
        if not results or len(results) == 0:
            print("⚠️ Vision: No subject detected")
            return image_bytes, time.time() - start
        
        # Generate mask
        observation = results[0]
        mask_buffer, error = observation.generateScaledMaskForImageForInstances_fromRequestHandler_error_(
            observation.allInstances(), handler, None
        )
        
        if error:
            print(f"⚠️ Vision: Mask generation failed - {error}")
            return image_bytes, time.time() - start
        
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

    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ Vision failed: {e}")
        
    return image_bytes, time.time() - start

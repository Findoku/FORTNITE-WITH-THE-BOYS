import photos
import io
import objc_util
import os

# Load Apple's Vision framework
objc_util.load_framework('Vision')
VNRecognizeTextRequest = objc_util.ObjCClass('VNRecognizeTextRequest')
VNImageRequestHandler = objc_util.ObjCClass('VNImageRequestHandler')
NSData = objc_util.ObjCClass('NSData')

def image_to_text(image):
    # Convert PIL image to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    byte_data = buffer.getvalue()

    # Convert to NSData for Vision framework
    ns_data = NSData.dataWithBytes_length_(byte_data, len(byte_data))

    # Create the text recognition request
    results = []

    def completion_handler(_cmd, request, error):
        observations = request.results()
        for i in range(observations.count()):
            observation = observations.objectAtIndex_(i)
            text = str(observation.topCandidates_(1).objectAtIndex_(0).string())
            results.append(text)

    handler_block = objc_util.ObjCBlock(
        completion_handler,
        restype=None,
        argtypes=[objc_util.c_void_p, objc_util.c_void_p, objc_util.c_void_p]
    )

    # Set up the request
    request = VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler_block)
    request.setRecognitionLevel_(1)  # 1 = accurate, 0 = fast

    # Run the request
    img_handler = VNImageRequestHandler.alloc().initWithData_options_(
        ns_data, objc_util.ns({})
    )
    img_handler.performRequests_error_(objc_util.ns([request]), None)

    return '\n'.join(results)


# --- Main ---
print('Opening camera...')
image = photos.capture_image()

if image is None:
    print('No photo taken.')
else:
    print('Running OCR...')
    text = image_to_text(image)
    
    if text:
        print('\n--- Extracted Text ---')
        print(text)
    else:
        print('No text found in image.')
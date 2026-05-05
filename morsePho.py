import photos
import io
import objc_util

def image_to_text(image):
    # Convert PIL image to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    byte_data = buffer.getvalue()

    # Load Vision framework
    objc_util.load_framework('Vision')
    
    NSData = objc_util.ObjCClass('NSData')
    VNRecognizeTextRequest = objc_util.ObjCClass('VNRecognizeTextRequest')
    VNImageRequestHandler = objc_util.ObjCClass('VNImageRequestHandler')

    # Convert image bytes to NSData
    ns_data = NSData.dataWithBytes_length_(byte_data, len(byte_data))

    # Create request WITHOUT a callback
    request = VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(0)  # 0 = fast, 1 = accurate

    # Run the handler
    handler = VNImageRequestHandler.alloc().initWithData_options_(
        ns_data, objc_util.ns({})
    )
    
    success = handler.performRequests_error_(objc_util.ns([request]), None)
    
    if not success:
        return 'OCR failed'

    # Extract results
    results = []
    observations = request.results()
    for i in range(observations.count()):
        obs = observations.objectAtIndex_(i)
        candidate = obs.topCandidates_(1).objectAtIndex_(0)
        results.append(str(candidate.string()))

    return '\n'.join(results)


# --- Main ---
print('Opening camera...')
image = photos.capture_image()

if image is None:
    print('No photo taken.')
else:
    print('Running OCR...')
    try:
        text = image_to_text(image)
        print('\n--- Extracted Text ---')
        print(text)
    except Exception as e:
        print(f'Error: {e}')
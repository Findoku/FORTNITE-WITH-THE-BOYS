import photos
import io
import objc_util
import requests
import json

def image_to_text(image):
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    byte_data = buffer.getvalue()

    objc_util.load_framework('Vision')
    NSData = objc_util.ObjCClass('NSData')
    VNRecognizeTextRequest = objc_util.ObjCClass('VNRecognizeTextRequest')
    VNImageRequestHandler = objc_util.ObjCClass('VNImageRequestHandler')

    ns_data = NSData.dataWithBytes_length_(byte_data, len(byte_data))
    request = VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(0)

    handler = VNImageRequestHandler.alloc().initWithData_options_(
        ns_data, objc_util.ns({})
    )
    handler.performRequests_error_(objc_util.ns([request]), None)

    results = []
    observations = request.results()
    for i in range(observations.count()):
        obs = observations.objectAtIndex_(i)
        candidate = obs.topCandidates_(1).objectAtIndex_(0)
        results.append(str(candidate.string()))

    return '\n'.join(results)


def extract_question_with_claude(raw_text):
    api_key = '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'  # get from console.anthropic.com
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 1024,
            'messages': [
                {
                    'role': 'user',
                    'content': f'''The following is raw OCR text extracted from a photo of a multiple choice question. 
There may be extra noise, page numbers, watermarks, or irrelevant text mixed in.

Please extract ONLY:
1. The question
2. The answer choices (A, B, C, D etc.)

Format it cleanly like:
Question: ...
A) ...
B) ...
C) ...
D) ...

Raw OCR text:
{raw_text}'''
                }
            ]
        }
    )
    
    data = response.json()
    return data['content'][0]['text']


# --- Main ---
print('Opening camera...')
image = photos.capture_image()

if image is None:
    print('No photo taken.')
else:
    print('Running OCR...')
    try:
        raw_text = image_to_text(image)
        print('Raw OCR output:')
        print(raw_text)
        
        print('\nCleaning up with Claude...')
        clean = extract_question_with_claude(raw_text)
        
        print('\n--- Extracted Question ---')
        print(clean)
        
    except Exception as e:
        print(f'Error: {e}')
import photos
import io
import objc_util
import requests
import json
import keychain 

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
    api_key = keychain.get_password('anthropic', 'api_key', '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')
    
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
                    'content': f'''Extract only the multiple choice question and answer choices from this raw OCR text. Format as Question: ... A) ... B) ... etc.

Raw text:
{raw_text}'''
                }
            ]
        }
    )
    
    # Print full response so we can see the error
    print('Status code:', response.status_code)
    print('Full response:', response.text)
    
    data = response.json()
    
    # Check for error in response
    if 'error' in data:
        return f"API Error: {data['error']['message']}"
    
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
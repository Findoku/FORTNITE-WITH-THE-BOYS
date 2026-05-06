import photos
import io
import objc_util
import requests     
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

def gemini(prompt):
    api_key = keychain.get_password('gemini', 'api_key')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}'

    response = requests.post(
        url,
        headers={'content-type': 'application/json'},
        json={
            'contents': [
                {
                    'parts': [
                        {'text': prompt}
                    ]
                }
            ]
        }
    )

    data = response.json()

    if 'error' in data:
        raise Exception(data['error']['message'])

    return data['candidates'][0]['content']['parts'][0]['text'].strip()


def format_question(raw_text):
    prompt = f'''You are a text parser. Below is raw OCR text taken from a photo of a multiple choice question.
It may contain noise, page numbers, watermarks, or garbled text.

Extract and reformat it cleanly like this:
Question: ...
A) ...
B) ...
C) ...
D) ...

Only include the question and answer choices. Nothing else.

Raw OCR text:
{raw_text}'''

    return gemini(prompt)


def get_answer(formatted_question):
    prompt = f'''You are answering a multiple choice question.

Rules:
- Respond with ONLY one character: A, B, C, or D
- Do NOT include explanation
- Do NOT include words
- Do NOT include punctuation

Question:
{formatted_question}'''

    return gemini(prompt)


# --- Main ---
print('Opening camera...')
image = photos.capture_image()

if image is None:
    print('No photo taken.')
else:
    try:
        print('Running OCR...')
        raw_text = image_to_text(image)

        print('Formatting question...')
        formatted = format_question(raw_text)
        print('\n--- Formatted Question ---')
        print(formatted)

        print('\nGetting answer...')
        answer = get_answer(formatted)
        print(f'\nAnswer: {answer}')

    except Exception as e:
        print(f'Error: {e}')

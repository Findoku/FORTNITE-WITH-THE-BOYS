import photos
import io
import objc_util
import requests     
import keychain
import os
import time


# Morse code dictionary
MORSE = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',    'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..',   'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',   'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-', 'R': '.-.',  'S': '...',  'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-',
    'Y': '-.--', 'Z': '--..'
}

# Timing constants (in seconds)
DOT      = 0.15
DASH     = 0.45
SYMBOL_GAP = 0.15
LETTER_GAP = 0.5


def vibrate_dot():
    UIImpactFeedbackGenerator = objc_util.ObjCClass('UIImpactFeedbackGenerator')
    gen = UIImpactFeedbackGenerator.alloc().initWithStyle_(2)
    gen.prepare()
    gen.impactOccurred()
    time.sleep(0.15)  # short buzz


def vibrate_dash():
    UIImpactFeedbackGenerator = objc_util.ObjCClass('UIImpactFeedbackGenerator')
    gen = UIImpactFeedbackGenerator.alloc().initWithStyle_(2)
    gen.prepare()
    # Fire multiple impacts rapidly to simulate a long buzz
    for _ in range(6):
        gen.impactOccurred()
        time.sleep(0.05)


def vibrate_morse(letter):
    letter = letter.strip().upper()
    if letter not in MORSE:
        print(f'No Morse code for: {letter}')
        return

    pattern = MORSE[letter]
    print(f'Vibrating Morse for {letter}: {pattern}')

    for i, symbol in enumerate(pattern):
        if symbol == '.':
            vibrate_dot()
        elif symbol == '-':
            vibrate_dash()

        # Gap between symbols
        if i < len(pattern) - 1:
            time.sleep(0.15)

    # Pause after full letter
    time.sleep(0.5)


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
(E or higher if you have to)

Only include the question and answer choices. Nothing else.

Raw OCR text:
{raw_text}'''

    return gemini(prompt)


def get_answer(formatted_question):
    prompt = f'''You are answering a multiple choice question.

Rules:
- Respond with ONLY one character: A, B, C, D (or E or higher if you have to)
- Do NOT include explanation
- Do NOT include words
- Do NOT include punctuation

Question:
{formatted_question}'''

    return gemini(prompt)


def save_to_file(formatted, answer):
    save_dir = os.path.expanduser('./')
    os.makedirs(save_dir, exist_ok=True)

    log_file = os.path.join(save_dir, 'questions_log.txt')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    entry = f'''
==========================================
{timestamp}
==========================================
{formatted}

Answer: {answer}
==========================================

'''

    with open(log_file, 'a') as f:
        f.write(entry)

    print(f'Saved to: {log_file}')



while True:
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

            save_to_file(formatted, answer)

            print(f'\nVibrating answer in Morse code: {answer}')
            vibrate_morse(answer)
            time.sleep(0.4)
            vibrate_morse(answer)
            time.sleep(0.4)
            vibrate_morse(answer)
            time.sleep(0.4)

        except Exception as e:
            print(f'Error: {e}')
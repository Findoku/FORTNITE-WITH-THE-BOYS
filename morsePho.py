import ui
import console
import clipboard
import photos
import io
import os

class Extracter(ui.View):
    def __init__(self):
        # Take Photo Button
        self.take_photo_btn = ui.Button(flex='LR', title='Take Photo')
        self.take_photo_btn.action = self.take_photo_action
        self.add_subview(self.take_photo_btn)

    @ui.in_background
    def take_photo_action(self, sender):
        image = photos.capture_image()
        
        if image is None:
            console.hud_alert('No photo taken', 'error', 1.0)
            return
        
        # Save to a BytesIO buffer
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        byte_data = buffer.getvalue()
        
        # Save the bytes to a file
        save_dir = os.path.expanduser('~/Documents/photos nmorse code/photos')
        os.makedirs(save_dir, exist_ok=True)
        
        import time
        filepath = os.path.join(save_dir, f'photo_{time.time()}.jpg')
        with open(filepath, 'wb') as f:
            f.write(byte_data)
        
        print(f'Saved {len(byte_data)} bytes to {filepath}')
        console.hud_alert('Photo saved!', 'success', 1.0)

if __name__ == '__main__':
    view = Extracter()
    view.present('sheet')
import ui
import console
import clipboard
import photos

class Extracter(ui.View):
    def __init__(self):
        # Take Photo Button
        self.take_photo_btn = ui.Button(flex='LR', title='Take Photo')
        self.take_photo_btn.action = self.take_photo_action
        self.add_subview(self.take_photo_btn)

    @ui.in_background
    def take_photo_action(self, sender):
        image = photos.capture_image()
        
        # Check if image is None before doing anything
        if image is None:
            console.alert('No photo taken', 'Please take a photo before saving.', 'OK', hide_cancel_button=True)
            return
        
        photos.save_image(image)
        console.hud_alert('Photo saved!', 'success', 1.0)

if __name__ == '__main__':
    view = Extracter()
    view.present('sheet')
import cv2
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App


class CameraViewfinder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        
        # Camera display widget
        self.image_widget = Image()
        self.add_widget(self.image_widget)

        # Control buttons
        button_layout = BoxLayout(size_hint_y=0.2)
        self.start_button = Button(text="Start Camera")
        self.start_button.bind(on_press=self.start_camera)
        button_layout.add_widget(self.start_button)

        self.stop_button = Button(text="Stop Camera", disabled=True)
        self.stop_button.bind(on_press=self.stop_camera)
        button_layout.add_widget(self.stop_button)

        self.record_button = Button(text="Record", disabled=True)
        self.record_button.bind(on_press=self.record_video)
        button_layout.add_widget(self.record_button)

        self.stop_record_button = Button(text="Stop Recording", disabled=True)
        self.stop_record_button.bind(on_press=self.stop_recording)
        button_layout.add_widget(self.stop_record_button)

        self.add_widget(button_layout)

        # Camera attributes
        self.capture = None
        self.recording = False
        self.out = None

    def start_camera(self, instance):
        self.capture = cv2.VideoCapture(0)  # Adjust index if necessary
        if not self.capture.isOpened():
            print("Failed to open camera")
            return

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.record_button.disabled = False

    def stop_camera(self, instance):
        if self.capture:
            Clock.unschedule(self.update)
            self.capture.release()
            self.image_widget.texture = None

        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.record_button.disabled = True
        self.stop_record_button.disabled = True

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.image_widget.texture = texture

    def record_video(self, instance):
        if self.capture and not self.recording:
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.out = cv2.VideoWriter("output.avi", fourcc, 20.0, (640, 480))
            self.recording = True
            self.record_button.disabled = True
            self.stop_record_button.disabled = False
            print("Recording started")

    def stop_recording(self, instance):
        if self.recording:
            self.recording = False
            self.out.release()
            self.record_button.disabled = False
            self.stop_record_button.disabled = True
            print("Recording stopped")

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Display frame
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.image_widget.texture = texture

            # Record frame if recording is active
            if self.recording:
                self.out.write(frame)


class CameraApp(App):
    def build(self):
        return CameraViewfinder()


if __name__ == "__main__":
    CameraApp().run()

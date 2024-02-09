import threading
from PIL import Image
import os
import time
from datetime import datetime
from PIL import Image

DIR = "/home/liam/dev/llm_task_planning/data/videos/"

class SaveImagesThread(threading.Thread):
    def __init__(self, controller, frame_rate=2, directory=DIR, planner=""):
        threading.Thread.__init__(self, target=self.run)
        if directory == DIR:
            directory += datetime.now().strftime("%Y%m%d_%H%M%S")
        self.directory = directory  # The directory to save the images
        self.controller = controller
        self.images = []
        self.frame_rate = frame_rate
        self.keep_running = True

    def join(self, timeout: float | None = ...) -> None:
        self.keep_running = False
        self.save_images()

    def reset(self):
        self.images = []
        self.keep_running = True
        self.start()

    def run(self):
        while self.keep_running:
            time.sleep(1/self.frame_rate)
            self.images.append(Image.fromarray(self.controller.last_event.frame).resize(size=(420, 210)))
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Save each image to the directory
        for idx, image in enumerate(self.images):
            image_path = os.path.join(self.directory, f'image_{idx}.png')
            image.save(image_path)
            print(f'Saved {image_path}')

    def save_images(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Save each image to the directory
        for idx, image in enumerate(self.images):
            image_path = os.path.join(self.directory, f'image_{idx}.png')
            image.save(image_path)
            print(f'Saved {image_path}')


import io
import requests
from PIL import Image
import json
import pygame


class WebbImage:
    def __init__(self, image_info):
        self.data = image_info
        self.date = self.get_date()
        self.url = self.get_url()
        self.pil_image = None

    def get_date(self):
        return self.data['Date']

    def get_description(self):
        pass
        # return self.data[self.index][]

    def get_url(self):
        return self.data['ReferenceURL']

    def get_image(self):
        image_url =  self.data["formats_url"]["large"]
        image_bytes = requests.get(image_url).content

        return io.BytesIO(image_bytes)



class Manager:
    def __init__(self):
        self.images = []
        self.current_index = 0  # 0 is present day, increasing it goes into the past
        self.load_data('data.json')

    def load_data(self, data_json):
        with open(data_json, "r", encoding="utf-8") as f:
            data = json.load(f)

            for image in data:
                self.images.append(WebbImage(image))

    def get_image(self):
        image = self.images[self.current_index].get_image()
        return image

    def next_image(self):
        if self.current_index != len(self.images) - 1:
            self.current_index += 1
        else:
            print("Images still loading, or have reached the end")

    def previous_image(self):
        if self.current_index != 0:
            self.current_index -= 1



class WebbFinderApp:
    def __init__(self, manager):
        self.manager = manager
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.need_redraw = True
        self.current_image = None
        self.change_image(self.manager.get_image())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.manager.next_image()
                    self.need_redraw = True
                if event.key == pygame.K_RIGHT:
                    self.manager.previous_image()
                    self.need_redraw = True

    def draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.current_image, (0, 0))
        pygame.display.flip()
        self.need_redraw = False

    def run(self):
        while self.running:
            self.handle_events()

            if self.need_redraw:
                self.draw()

    def change_image(self, new_image):
        self.current_image = pygame.image.load(new_image)


"""
url = "https://esawebb.org/images/json/page/1/?&sort=-release_date"
response = requests.get(url)
data = response.json()
"""


if __name__ == "__main__":
    manager_app = Manager()

    app = WebbFinderApp(manager_app)
    app.run()
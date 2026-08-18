import io
import requests
import webbrowser
import json
import threading
import pygame


class Button:
    def __init__(self, text, x, y, width, height, normal_color=(132, 132, 132), hover_color=(164, 164, 164), text_color=(200, 200, 200), font_size=32):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color

        self.font = pygame.font.SysFont(None, font_size)
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        self.hover = False

    def draw(self, surface):
        if self.hover:
            color = self.hover_color
        else:
            color = self.normal_color

        pygame.draw.rect(surface, color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover

    def clicked(self, mouse_pos, event):
        if self.rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                return True
        return False


class Url:
    def __init__(self, text, url, pos, font_size=18, color=(0, 88, 248), hover_color=(31, 102, 202)):
        self.text = text
        self.url = url
        self.pos = pos
        self.font = pygame.font.SysFont(None, font_size)

        self.base_color = color
        self.hover_color = hover_color
        self.current_color = color

        self.text_surface = self.font.render(self.text, True, self.current_color)
        self.rect = self.text_surface.get_rect(topleft=pos)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    webbrowser.open(self.url)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if not self.is_hovered:
                self.is_hovered = True
                self.current_color = self.hover_color
                self.text_surface = self.font.render(self.text, True, self.current_color)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.text_surface = self.font.render(self.text, True, self.current_color)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, surface):
        surface.blit(self.text_surface, self.rect)
        pygame.draw.line(surface, self.current_color, (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom), 2)

class WebbImage:
    def __init__(self, image_info):
        self.data = image_info
        self.title = self.data['Title'][2:-1]
        self.description = self.data['Description']
        self.date = self.data['Date']
        self.url = self.data['ReferenceURL']
        self.stored_image = None

    def get_image(self, session):
        if not self.stored_image:
            image_url =  self.data["formats_url"]["screen640"]
            image_bytes = session.get(image_url).content
            self.stored_image = image_bytes

        return io.BytesIO(self.stored_image)



class Manager:
    def __init__(self):
        self.images = []
        self.current_index = 0  # 0 is present day, increasing it goes into the past
        self.current_image = None
        self.session = requests.Session()
        self.fetching_data = True
        self.load_stored_data()
        self.load_data()
        self.update_current_image()

    def load_stored_data(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

                for image in data:
                    self.images.append(WebbImage(image))

        except FileNotFoundError:
            print("No data.json found. Downloading all info from the web. This WILL take a while (around 30-40 second per 100 images)")

    def load_data(self):
        thread = threading.Thread(target=self.download_data)
        thread.start()

    def download_data(self):
        print("Checking for new images from the stars... (this might take a moment)")

        existing_urls = {img.url for img in self.images} # each url is unique to each image, just a fast way to identify each image
        new_images = [] # list of new images needed to be added. not just appended to the list because then it wouldnt be in chronological order
        no_data = not self.images
        fetching_data = True
        current_page = 1

        while fetching_data:
            url = f"https://esawebb.org/images/json/page/{current_page}/?&sort=-release_date"

            try:
                response = self.session.get(url)

                if response.status_code != 200:
                    break

                data = response.json()

                last_image = False # boolean for if the latest image stored in the json has been reached (i.e., all caught up)

                if not data:
                    print("End of library of images :(")
                    break

                for image_info in data:
                    ref_url = image_info.get("ReferenceURL")

                    if ref_url in existing_urls:
                        last_image = True
                        break
                    else:
                        if no_data:
                            if not self.images:
                                self.images.append(WebbImage(image_info))
                                self.update_current_image()
                            else:
                                self.images.append(WebbImage(image_info))

                        new_images.append(WebbImage(image_info))

                if last_image:
                    print("All images found, everything is up to date")
                    break

                print(f"Page {current_page} has successfully been loaded")
                current_page += 1

            except requests.exceptions.RequestException as error:
                print(f"Lost connection: {error}")
                break

        if new_images:
            if not no_data:
                self.images = new_images + self.images
            self.current_index += len(new_images) # so the user stays on the same image they already are on
            print("Saving data...")
            self.save_data()
            print("Saved! Your next session will open much quicker")

    def save_data(self):
        raw_data = [img.data for img in self.images]

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)

    def update_current_image(self):
        if self.images:
            self.current_image = self.images[self.current_index]

    def get_image(self):
        image = self.current_image.get_image(self.session)
        return image

    def next_image(self):
        if self.current_index != len(self.images) - 1:
            self.current_index += 1
            self.update_current_image()
        else:
            print("Images still loading, or have reached the end")

    def previous_image(self):
        if self.current_index != 0:
            self.current_index -= 1
            self.update_current_image()


class WebbFinderApp:
    def __init__(self, manager):
        self.manager = manager
        pygame.init()

        self.screen = pygame.display.set_mode((700, 640)) # 700x640
        self.running = True
        self.need_redraw = True
        self.current_image = None
        self.title = None
        self.description = None
        self.date = None
        self.link = None
        self.change_image()

        self.previous_button = Button("<", 30, 560, 50, 50)
        self.next_button = Button(">", 620, 560, 50, 50)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        self.link.update(mouse_pos)
        self.previous_button.check_hover(mouse_pos)
        self.next_button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.next_image()
                if event.key == pygame.K_RIGHT:
                    self.previous_image()

            if self.next_button.clicked(mouse_pos, event):
                self.previous_image()

            if self.previous_button.clicked(mouse_pos, event):
                self.next_image()

            self.link.handle_event(event)

    def next_image(self):
        self.manager.next_image()
        self.change_image()
        self.need_redraw = True

    def previous_image(self):
        self.manager.previous_image()
        self.change_image()
        self.need_redraw = True

    def draw(self):
        if self.need_redraw:
            self.screen.fill((0,0,0))
            pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, 700, 640))
            # pygame.draw.rect(self.screen, (60, 60, 60), (30, 410, 640, 130))
            self.screen.blit(self.current_image, (30, 30))
            self.draw_text()
            self.need_redraw = False

        pygame.draw.rect(self.screen, (0, 0, 0), (30, 560, 50, 50))
        pygame.draw.rect(self.screen, (0, 0, 0), (620, 560, 50, 50))
        self.draw_buttons()

        pygame.draw.rect(self.screen, (40, 40, 40), self.link.rect)
        self.link.draw(self.screen)
        pygame.display.flip()

    def draw_buttons(self):
        self.previous_button.draw(self.screen)
        self.next_button.draw(self.screen)

    def draw_text(self):
        font = pygame.font.SysFont(None, 24)

        text_surface = font.render(self.title, True, (255, 255, 255))
        text_rect = text_surface.get_rect()

        text_rect.center = (350, 580)
        self.screen.blit(text_surface, text_rect)

        font = pygame.font.SysFont(None, 18)

        text_surface = font.render(self.date, True, (255, 255, 255))
        text_rect = text_surface.get_rect()

        text_rect.center = (350, 600)
        self.screen.blit(text_surface, text_rect)

        self.draw_description()

    def draw_description(self):
        font = pygame.font.SysFont(None, 18)

        text = self.description[2:-1]
        words = text.split(' ')
        lines = []
        current_line = ""
        text_box = pygame.Rect(30, 410, 640, 130)

        for word in words:
            test_line = current_line + word + " "

            if font.size(test_line)[0] < text_box.width and len(lines) < 8:
                current_line = test_line
            else:
                if len(lines) == 7:
                    lines.append(current_line[:-1] + '...')
                elif len(lines) == 8:
                    pass
                else:
                    lines.append(current_line)
                    current_line = word + " "

        if len(lines) < 8:
            lines.append(current_line) # the last line

        line_height = font.get_linesize()
        line_pos = text_box.y

        for line in lines:
            text_surface = font.render(line.strip(), True, (255, 255, 255))
            self.screen.blit(text_surface, (text_box.x, line_pos))

            line_pos += line_height

    def draw_loading_screen(self):
        self.screen.fill((8, 8, 16))

        font = pygame.font.SysFont(None, 48)
        text_surf = font.render("Fetching images from the stars...", True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(350, 200))
        self.screen.blit(text_surf, text_rect)

        current_time = pygame.time.get_ticks()
        num_stars = (current_time // 500) % 4 # either 0, 1, 2 or 3 stars -> animation for waiting

        for star in range(num_stars):
            font = pygame.font.SysFont(None, 48 + 8 * star)
            star_surf = font.render("*", True, (255, 255, 100))
            x = 350 + star*80
            y = 360 - star*40
            star_rect = star_surf.get_rect(center=(x, y))
            self.screen.blit(star_surf, star_rect)

        center_x, center_y = 180, 480

        pygame.draw.line(self.screen, (150, 150, 150), (center_x, center_y), (center_x - 30, center_y + 100), 5)
        pygame.draw.line(self.screen, (150, 150, 150), (center_x, center_y), (center_x + 30, center_y + 100), 5)
        pygame.draw.line(self.screen, (100, 100, 100), (center_x, center_y), (center_x, center_y + 100), 5)

        pygame.draw.polygon(self.screen, (220, 220, 220), [
            (center_x - 40, center_y + 20),
            (center_x + 50, center_y - 20),
            (center_x + 40, center_y - 40),
            (center_x - 50, center_y)
        ])
        pygame.draw.circle(self.screen, (100, 150, 255), (center_x + 45, center_y - 30), 12)

        pygame.display.flip()

    def run(self):
        was_loading = not self.manager.images

        while self.running:
            if self.manager.images:
                if was_loading:
                    self.change_image()
                    was_loading = False

                self.handle_events()
                self.draw_buttons()
                self.draw()

            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                self.draw_loading_screen()

    def change_image(self):
        if self.manager.images:
            new_image = self.manager.get_image()
            self.current_image = pygame.image.load(new_image)

            self.title = self.manager.current_image.title
            self.description = self.manager.current_image.description
            self.date = self.manager.current_image.date
            self.link = Url(f"More info at: {self.manager.current_image.url}",
                            self.manager.current_image.url,(30, 530), )

        else:
            pass


"""
url = "https://esawebb.org/images/json/page/1/?&sort=-release_date"
response = requests.get(url)
data = response.json()
"""


if __name__ == "__main__":
    manager_app = Manager()

    app = WebbFinderApp(manager_app)
    app.run()
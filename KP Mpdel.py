from manim import *

# === CONFIG ===
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30

class Thumbnail(Scene):
    def construct(self):
        self.camera.background_color = "#0B0C10"  # deep navy

        # KP Model Graph Image
        graph = ImageMobject("Screenshot 2026-01-17 144028.png")
        graph.scale(0.1)
        graph.to_edge(LEFT)

        # Title Block
        title = Text("Kronig–Penney Model", font_size=72, color="#FFD700", weight=BOLD)
        subtitle = Text("Band Theory of Solids", font_size=54, color="#00FFFF")
        tagline = Text("Explained Clearly!", font_size=60, color="#FF4500")

        # Stack text vertically
        text_block = VGroup(title, subtitle, tagline).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_block.to_edge(RIGHT).shift(UP * 0.5)

        # Logo watermark
        logo = Text("SCJ Physics", font_size=36, color="#FFFFFF")
        logo.to_corner(DR)

        # Add all elements
        self.add(graph, text_block, logo)
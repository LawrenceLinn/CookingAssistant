import base64
from io import BytesIO

# from IPython.display import HTML, display
from PIL import Image





file_path = "../../../static/img/ollama_example_img.jpg"
pil_image = Image.open(file_path)
image_b64 = convert_to_base64(pil_image)
plt_img_base64(image_b64)

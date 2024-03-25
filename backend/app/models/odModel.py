import torch
import torchvision
import torchvision.transforms as T
from PIL import Image
import io
import base64

def bytes2img(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image

def read_image(path):
    image = Image.open(path)
    return image

def save_image(image, path):
    image.save(path)

def img2tensor(image):
    transform = T.Compose([ 
        T.PILToTensor() 
    ]) 
    img_tensor = transform(image) 
    return img_tensor

def img2bytes(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

def img2b64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def odModel(img):

    ingredients = ['A', 'B']
    # tensor = torch.rand(3,256,256)
    # transform = T.Compose([ 
    #         T.PILToTensor() 
    # ]) 
    # img = transform(img)

    return {'ingredients':ingredients, 'image':img}
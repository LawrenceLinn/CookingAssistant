import torch
import torchvision
import torchvision.transforms as T
from PIL import Image
import io

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
    print(type(imgByteArr))
    return imgByteArr

def odModel(img):

    ingredients = ['A', 'B']
    # tensor = torch.rand(3,256,256)
    # transform = T.Compose([ 
    #         T.PILToTensor() 
    # ]) 
    # img = transform(img)

    return {'ingredients':ingredients, 'image':img}
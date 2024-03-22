import torch
import torchvision
import torchvision.transforms as T
from PIL import Image

def Model(img):

    ingredients = ['A', 'B']
    # tensor = torch.rand(3,256,256)
    # transform = T.Compose([ 
    #         T.PILToTensor() 
    # ]) 
    # img = transform(img)

    return {'ingredients':ingredients, 'image':img}
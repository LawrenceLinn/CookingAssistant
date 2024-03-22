from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from .auth.auth import get_hashed_password
from .config.config import settings
from .models.users import User
from .routers.api import api_router
from .routers.offer import router as offer_router

import cv2
import numpy as np

from PIL import Image
import io
import torchvision.transforms as transforms 

from app.test_model import Model
from app.test_lang_model import LangModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup mongoDB
    app.client = AsyncIOMotorClient(
        settings.MONGO_HOST,
        settings.MONGO_PORT,
        username=settings.MONGO_USER,
        password=settings.MONGO_PASSWORD,
    )
    await init_beanie(database=app.client[settings.MONGO_DB], document_models=[User])

    user = await User.find_one({"email": settings.FIRST_SUPERUSER})
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_hashed_password(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
        )
        await user.create()

    # yield app
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.itemID = 0

# Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     # See https://github.com/pydantic/pydantic/issues/7186 for reason of using rstrip
    #     str(origin).rstrip("/")
    #     for origin in settings.BACKEND_CORS_ORIGINS
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# def process_video_data(data):
#     #将 byte stream 转换为视频帧
#     nparr = np.fromstring(data, np.uint8)
#     img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     cv2.imshow('frame', img_np)
#     return data  # 返回处理后的数据


# @app.websocket("/ws/video")
# async def websocket_video(websocket: WebSocket):
#     # print in the console
#     print("websocket_video")
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_bytes()
#         # 对视频数据进行处理
#         # print("data")
#         # 这里是处理逻辑的伪代码
#         processed_data = process_video_data(data)
#         # 将处理后的视频数据发送回客户端
#         await websocket.send_bytes(processed_data)
#         # 使用 cv 实时输出视频



# @app.websocket("/ws/audio")
# async def websocket_audio(websocket: WebSocket):
#     # print in the console
#     print("websocket_audio0")
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_bytes()
#         # 对音频数据进行处理
#         # print(data)
#         # 这里是处理逻辑的伪代码
#         processed_data = process_video_data(data)
#         # 将处理后的音频数据发送回客户端
#         await websocket.send_bytes("Frame Received")
        

@app.websocket("/ws/text")
async def websocket_endpoint(websocket: WebSocket, item_id:str = Query(None)):
    await websocket.accept()
    if item_id:
        # Read user input image by id
        print('Query:', item_id)
        img = Image.open('images/'+item_id+'.jpg')

        # Pass image to model
        model_result = Model(img)
        
        # Convert model output to byte array
        model_img = model_result['image']
        img_byte_arr = io.BytesIO()
        model_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Send to frontend
        await websocket.send_bytes(img_byte_arr)
        
    while True:
        # Read user input
        data = await websocket.receive_text()
        # Pass to lang model
        print(data)
        # Send to frontend
        await websocket.send_text(f'ChatBot: {LangModel(data)}')


@app.websocket("/ws/image")
async def image(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected for image processing")
    while True:
        data = await websocket.receive_bytes()

        # Process the image data
        image = Image.open(io.BytesIO(data))
        width, height = image.size
        
        # Here, you can save the image, analyze it, etc.
        # For demonstration, we'll just send back its dimensions

        # image.save('test.jpg')
        transform = transforms.Compose([ 
            transforms.PILToTensor() 
        ]) 

        img_tensor = transform(image) 
        
        # await websocket.send_text(f"Image Received: {width}x{height}px, {img_tensor}, {img_tensor.size()}")
        await websocket.send_text(f"Image Received: {img_tensor.size()} {img_tensor}")

@app.websocket("/ws/imageCapture")
async def imageCapture(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected for image processing")
    i = 0
    while True:
        i += 1
        print(app.itemID)
        image_data = await websocket.receive_bytes()
            
        # Convert the bytes to a PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Optionally, save the image to disk
        image.save('images/'+str(app.itemID)+".jpg")
        item_id = str(app.itemID)
        app.itemID += 1
        
        transform = transforms.Compose([ 
            transforms.PILToTensor() 
        ]) 
            
        img_tensor = transform(image) 

        # Send back a confirmation message with image dimensions
        print(i)
        print(img_tensor.size())
        await websocket.send_text(f"Image received: {img_tensor}")
        new_url = "/text" + '?item_id=' + item_id
            
        # await websocket.send_text(f"redirect:{new_url}")
        await websocket.send_json({"redirect": new_url, "data": img_tensor.size()})
        break
    
    return            

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(offer_router, prefix="", tags=["offer"])
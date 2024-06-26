from fastapi import APIRouter, HTTPException, WebSocket, Query
from ..models.langModel import load_model, LangModel

# from ..models.test_model import load_model, LangModel
from ..models.yolo.YOLO_V8 import YOLO_model
from ..models.Fast_RCNN.rcnn import rcnn_model
from ..models.odModel import (
    bytes2img,
    read_image,
    save_image,
    img2tensor,
    img2bytes,
    odModel,
    array2bytes,
)
from ..models.recipe_recommender_agent import create_agent_executor

router = APIRouter()

router.itemID = 0


@router.websocket("/ws/imageCapture")
async def imageCapture(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected for image processing")
    i = 0
    while True:
        i += 1
        # Receive the image data
        image_data = await websocket.receive_bytes()
        model_data = await websocket.receive_text()

        # Convert the bytes to a PIL Image
        image = bytes2img(image_data)

        # Optionally, save the image to disk
        save_image(image, f"images/{str(router.itemID)}.jpg")

        item_id = str(router.itemID)
        router.itemID += 1

        img_tensor = img2tensor(image)

        print("model data", model_data)
        if model_data == "yolo":
            new_url = f"/text?item_id={item_id}&model=0"
        else:
            new_url = f"/text?item_id={item_id}&model=1"

        # await websocket.send_text(f"redirect:{new_url}")
        await websocket.send_json({"redirect": new_url, "data": img_tensor.size()})
        break

    return


@router.websocket("/ws/text")
async def websocket_endpoint(
    websocket: WebSocket, item_id: str = Query(None), model: str = Query(None)
):
    await websocket.accept()
    if item_id:
        # Read user input image by id
        print("Query:", item_id)
        img = read_image(f"images/{item_id}.jpg")

        if model == "1":
            # FastRCNN
            print("rcnn")
            model_result = rcnn_model(f"images/{item_id}.jpg")
            img_byte_arr = array2bytes(model_result["image"])

        else:
            # YOLO
            print("yolo")
            model_result = YOLO_model(img)
            img_byte_arr = img2bytes(model_result["image"])

        # Send to frontend
        ingredients = ", ".join(model_result["ingredients"])
        await websocket.send_text(f"ingredients: {ingredients}")
        await websocket.send_bytes(img_byte_arr)

    agent_excutor = create_agent_executor()
    chat_history = []
    first = True
    while True:
        # Read user input
        user_input = await websocket.receive_text()
        if first:
            # Load model
            user_input = f"I have {ingredients}, {user_input}"
            first = False
        result = agent_excutor.invoke(
            {"input": user_input, "chat_history": chat_history}
        )
        chat_history.append((user_input, result["output"]))
        output = result["output"]
        await websocket.send_text(f"{output}")


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


# @router.websocket("/ws/image")
# async def image(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connected for image processing")
#     while True:
#         data = await websocket.receive_bytes()

#         # Process the image data
#         image = Image.open(io.BytesIO(data))
#         width, height = image.size

#         # Here, you can save the image, analyze it, etc.
#         # For demonstration, we'll just send back its dimensions

#         # image.save('test.jpg')
#         transform = transforms.Compose([
#             transforms.PILToTensor()
#         ])

#         img_tensor = transform(image)

#         # await websocket.send_text(f"Image Received: {width}x{height}px, {img_tensor}, {img_tensor.size()}")
#         await websocket.send_text(f"Image Received: {img_tensor.size()} {img_tensor}")

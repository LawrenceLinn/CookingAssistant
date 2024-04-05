import cv2
import torch
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import torchvision
import pandas as pd
import torchvision.transforms.functional as F


class ImageObjectDetector:

    def __init__(self, model, label_map, device):
        # self.model = model.to(device)
        self.model = model
        self.device = device
        self.label_map = label_map
        # Inverting the label_map for reverse lookup
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}

    def predict_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img_tensor = F.to_tensor(img).unsqueeze(0)
        # img_tensor = img_tensor.to(self.device)

        self.model.eval()
        with torch.no_grad():
            predictions = self.model(img_tensor)

        predictions = [{k: v.to('cpu') for k, v in t.items()} for t in predictions]
        prediction = predictions[0]

        return prediction

    def draw_boxes_on_image(self, image_path, boxes, labels, scores, threshold=0.4):
        image = cv2.imread(image_path)
        image_with_boxes = cv2.resize(image, (400, 400))
        orig_h, orig_w, _ = image_with_boxes.shape

        # List to store unique labels in this photo
        high_confidence_labels = []

        # List to store labels with high confidence
        items = []
        # List to store labels with their probailities
        probabilities = []
        # List to store labels with their ids
        ids = []
        # Inilital Counter
        counter = 1

        for box, label, score in zip(boxes, labels, scores):
            if score < threshold:
                continue

            item_id = counter
            counter += 1

            box = box.int().numpy()
            start_point = (int(box[0] * orig_w / 256), int(box[1] * orig_h / 256))
            end_point = (int(box[2] * orig_w / 256), int(box[3] * orig_h / 256))

            cv2.rectangle(image_with_boxes, start_point, end_point, (0, 255, 0), 2)

            label_name = self.reverse_label_map[label.item()]
            if label_name not in high_confidence_labels:
               high_confidence_labels.append(label_name)  # Add label to the list

            label_score = f'{item_id}. {label_name}: {score.item():.2f}'

            # Add label to the list
            items.append(f"{label_name}")
            # Add probability to the list
            probabilities.append(score.item())
            # Add id to the list
            ids.append(item_id)

            # Calculate text size for background rectangle
            text_size = cv2.getTextSize(label_score, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text_bg_rect_start = (start_point[0], end_point[1] - text_size[1] - 5)
            text_bg_rect_end = (start_point[0] + text_size[0], end_point[1])
            # text_bg_rect_start = (start_point[0], start_point[1] - text_size[1] - 5)
            # text_bg_rect_end = (start_point[0] + text_size[0], start_point[1])

            # Draw white background rectangle
            cv2.rectangle(image_with_boxes, text_bg_rect_start, text_bg_rect_end, (255, 255, 255), -1)

            # Draw text
            # cv2.putText(image, label_score, (start_point[0], start_point[1] - 5),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            cv2.putText(image_with_boxes, label_score, (start_point[0], end_point[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        plt.figure(figsize=(6, 6))
        plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

        print("-----------------------------------------")

        # Create a DataFrame to store the results
        results_df = pd.DataFrame({
            'ID': ids,
            'Item and Probability': items,
            'Probability': probabilities
        })

        # Display the DataFrame
        display(HTML(results_df.to_html(index=False)))

        # print("Unique Ingredients from this photo:")
        # for i, label in enumerate(high_confidence_labels):
        #     # Print the label
        #     print(f'{i+1}. {label}')

        # Return Unique List and Image with Boxes
        return high_confidence_labels, cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)

    def detect_and_draw_boxes(self, image_path, threshold=0.5, iou_threshold=0.75):
        prediction = self.predict_image(image_path)
        # Directly use the tensors without unnecessary conversion
        boxes = prediction['boxes']
        scores = prediction['scores']
        labels = prediction['labels']

        # Sort and NMS
        sorted_indices = torch.argsort(scores, descending=True)
        boxes = boxes[sorted_indices]
        scores = scores[sorted_indices]
        labels = labels[sorted_indices]

        # keep = torchvision.ops.nms(boxes, scores, nms_threshold)

        # Initialize a mask to keep track of which boxes to keep
        keep = torch.ones_like(scores, dtype=torch.bool)

        # Loop through the boxes
        for i in range(boxes.size(0)):
            if keep[i] == 1:
            # Compute IoU with all other boxes
              ious = torchvision.ops.box_iou(boxes[i].unsqueeze(0), boxes).squeeze(0)
              # Filter out boxes with IoU > 0.3
              keep[i+1:] = keep[i+1:] & (ious[i+1:] < iou_threshold)

        final_boxes = boxes[keep]
        final_scores = scores[keep]
        final_labels = labels[keep]

        return self.draw_boxes_on_image(image_path, final_boxes, final_labels, final_scores, threshold)
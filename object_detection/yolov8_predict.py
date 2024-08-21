from ultralytics import YOLO
import cv2

model = YOLO("runs/train/weights/best.pt")

# from ndarray
img = cv2.imread("datasets/defect/valid/11.jpg")
results = model.predict(source=img, project='./runs', save=True, save_txt=True, show=True)  # save predictions as labels
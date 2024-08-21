from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

    # Use the model
    model.train(data="configs/defect.yaml", project='./runs', epochs=100, fliplr=0.0)  # train the model
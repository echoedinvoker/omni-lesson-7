import omni.replicator.core as rep
from omni.isaac.range_sensor import _range_sensor
import omni.kit.commands
import os
from pxr import Sdf, Usd
import time
import numpy as np
import cv2
from datetime import datetime
from ultralytics import YOLO


def setup(db: og.Database):
    state = db.per_instance_state
    camera_path = db.inputs.camera_path
    render_product = rep.create.render_product(camera_path, resolution=(256, 256))

    state.rgb_annotator = rep.AnnotatorRegistry.get_annotator("rgb")
    state.rgb_annotator.attach([render_product])

    state.lidarInterface = _range_sensor.acquire_lidar_sensor_interface()
    state.lidarPath = db.inputs.lidar_path

    state.is_triggered = False
    state.last_time = time.time()

    parent_path = "/".join(camera_path.split("/")[:-1])
    state.conveyor_speed_property = f"{parent_path}/ConveyorBeltGraph/ConveyorNode.inputs:velocity"
    state.conveyor_name = parent_path.split("/")[2]

    manager = omni.kit.app.get_app().get_extension_manager()
    extension_data_path = os.path.join(manager.get_extension_path_by_module("defect_detection"), "data")
    
    # 第一次predict會花比較長時間, 所以在這個階段先做完
    model_path = os.path.join(extension_data_path, "defect_detection_model.pt")
    state.model = YOLO(model_path)
    warming_up_image = cv2.imread(os.path.join(extension_data_path, "warming_up.jpg"))
    results = state.model(warming_up_image)


def cleanup(db: og.Database):
    pass


def compute(db: og.Database):
    state = db.per_instance_state
    if time.time() - state.last_time > 1:
        # 取得光達資料
        depth = np.sum(state.lidarInterface.get_linear_depth_data(state.lidarPath))

        if depth < 10 and state.is_triggered == False:
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 取得圖片資料
            rgb = state.rgb_annotator.get_data(device="cuda").numpy()

            # 轉為 BGR
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGBA2BGR)

            # 模型預測
            results = state.model(bgr)  # predict on an image
            result = results[0]

            # 處理預測結果
            boxes = result.boxes
            objects_len = len(result)
            if objects_len == 0:
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(state.conveyor_speed_property),
                    value=200,
                    prev='')
                image_save_dir = os.path.join(db.inputs.result_images_dir, "normal_images")
                image_path = os.path.join(image_save_dir, f"{state.conveyor_name}-{current_datetime}.png")
            else:
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(state.conveyor_speed_property),
                    value=-200,
                    prev='')
                for i in range(objects_len):
                    bounding_box = np.array(boxes.xyxy[i].cpu(), dtype=int)
                    top_left = (bounding_box[0], bounding_box[1])
                    bottom_right = (bounding_box[2], bounding_box[3])
                    cv2.rectangle(bgr, top_left, bottom_right, (0, 0, 255), 3, cv2.LINE_AA)
                image_save_dir = os.path.join(db.inputs.result_images_dir, "defect_images")
                image_path = os.path.join(image_save_dir, f"{state.conveyor_name}-{current_datetime}.png")
            cv2.imwrite(image_path, bgr)

            state.is_triggered = True
        elif depth >= 10:
            state.is_triggered = False

        state.last_time = time.time()
    return True
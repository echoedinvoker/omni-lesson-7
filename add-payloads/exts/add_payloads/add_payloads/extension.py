import omni.ext
import omni.ui as ui
import os
import pandas as pd
import numpy as np
import cv2
import omni.kit.commands
from pxr import UsdGeom, Sdf
import omni.graph.core as og


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[add_payloads] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Add_payloadsExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[add_payloads] add_payloads startup")
        manager = omni.kit.app.get_app().get_extension_manager()
        extension_data_path = os.path.join(manager.get_extension_path_by_module("add_payloads"), "data")

        self._count = 0

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("Add Payload Test", height=50)
                string_model = ui.SimpleStringModel("/home/aibox/AppRun/lesson_7/add-payloads/exts/add_payloads/add_payloads/layout_v2.png")
                ui.StringField(model=string_model, height=50)


                def on_click():
                    # Read image
                    image = cv2.imread(string_model.as_string)
                    stage = omni.usd.get_context().get_stage()
                    UsdGeom.SetStageMetersPerUnit(stage, 0.01)
                    stage_w, stage_h = image.shape[1], image.shape[0]

                    # Create dome light
                    omni.kit.commands.execute('CreatePrim',
                        prim_type='DomeLight',
                        attributes={'inputs:intensity': 1000, 'inputs:texture:format': 'latlong'})

                    # Create ground plane
                    omni.kit.commands.execute('CreatePayload',
                        usd_context=omni.usd.get_context(),
                        path_to='/World/gray_ground',
                        asset_path=os.path.join(extension_data_path, 'gray_ground.usd'),
                        instanceable=False)

                    # Create ground plane
                    omni.kit.commands.execute('CreatePayload',
                        usd_context=omni.usd.get_context(),
                        path_to='/World/cardbox',
                        asset_path=os.path.join(extension_data_path, 'cardbox.usd'),
                        instanceable=False)
                    omni.kit.commands.execute('DeletePrims',
                        paths=['/World/cardbox'],
                        destructive=False)

                    # Scale and move ground plane
                    omni.kit.commands.execute('TransformMultiPrimsSRTCpp',
                        count=1,
                        paths=['/World/gray_ground'],
                        new_translations=[stage_w / 2, -1 * stage_h / 2, 0.0],
                        new_rotations_eulers=[0.0, -0.0, 0.0],
                        new_rotations_orders=[0, 1, 2],
                        new_scales=[stage_w, stage_h, 1.0],
                        old_translations=[0.0, 0.0, 0.0],
                        old_rotations_eulers=[0.0, -0.0, 0.0],
                        old_rotations_orders=[0, 1, 2],
                        old_scales=[1.0, 1.0, 1.0],
                        usd_context_name='',
                        time_code=0.0)

                    # Create all components
                    template_image_dir = os.path.join(extension_data_path, 'template_image')
                    for image_name in os.listdir(template_image_dir):
                        template_image_path = os.path.join(template_image_dir, image_name)
                        template_image = cv2.imread(template_image_path)
                        h, w = template_image.shape[0], template_image.shape[1]


                        # Apply template Matching
                        res = cv2.matchTemplate(image, template_image, cv2.TM_CCOEFF_NORMED)
                        threshold = 0.9
                        loc = np.where(res >= threshold)

                        # Choose target point and create payload
                        processed_point_list = [np.array((-10000, -10000))]
                        distance_threshold = 30
                        count = 0

                        for pt in zip(*loc[::-1]):
                            target_x = pt[0] + int(w / 2)
                            target_y = pt[1] + int(h / 2)
                            target_point = np.array((target_x, target_y))
                            min_distance = 9999999
                            for processed_point in processed_point_list:
                                distance = np.linalg.norm(target_point - processed_point)
                                if distance < min_distance:
                                    min_distance = distance

                            if min_distance > distance_threshold:
                                x = float(target_point[0])
                                y = -1 * float(target_point[1])
                                z = 0.0
                                prim_path = f"/World/{image_name[:-4]}_{count}"
                                shape_name = f"{image_name[:-4]}".capitalize()

                                omni.kit.commands.execute('CreatePayload',
                                    usd_context=omni.usd.get_context(),
                                    path_to=prim_path,
                                    asset_path=os.path.join(extension_data_path, f"{image_name[:-4]}.usd"),
                                    instanceable=True)

                                omni.kit.commands.execute('TransformMultiPrimsSRTCpp',
                                    count=1,
                                    paths=[prim_path],
                                    new_translations=[x, y, z],
                                    new_rotation_eulers=[0.0, -0.0, 180.0],
                                    new_rotation_orders=[0, 1, 2],
                                    new_scales=[h, h, h],
                                    old_translations=[0.0, 0.0, 0.0],
                                    old_rotation_eulers=[0.0, -0.0, 0.0],
                                    old_rotation_orders=[0, 1, 2],
                                    old_scales=[1.0, 1.0, 1.0],
                                    usd_context_name='',
                                    time_code=0.0)

                                processed_point_list.append(target_point)
                                count += 1

                                if image_name[:-4] == 'conveyor_start':
                                    keys = og.Controller.Keys
                                    print('tst')
                                    (graph_handle, list_of_nodes, _, _) = og.Controller.edit(
                                        {"graph_path": f"/action_graph_{count}", "evaluator_name": "execution"},
                                        {
                                            keys.CREATE_NODES: [
                                                ("on_playback_tick", "omni.graph.action.OnPlaybackTick"),
                                                ("script_node", "omni.graph.scriptnode.ScriptNode"),
                                                ("on_stage_event", "omni.graph.action.OnStageEvent"),
                                                ("delete_box_node", "omni.graph.scriptnode.ScriptNode")
                                            ],
                                            keys.CREATE_ATTRIBUTES: [
                                                ("script_node.inputs:location", "pointd[3]"),
                                                ("script_node.inputs:index", "int"),
                                                ("delete_box_node.inputs:graph_path", "string")
                                            ],
                                            keys.SET_VALUES: [
                                                ("script_node.inputs:usePath", True),
                                                ("script_node.inputs:scriptPath", os.path.join(extension_data_path, "createbox.py")),
                                                ("script_node.inputs:location", (x, y, z)),
                                                ("script_node.inputs:index", count),
                                                ("on_stage_event.inputs:eventName", "Simulation Stop Play"),
                                                ("delete_box_node.inputs:usePath", True),
                                                ("delete_box_node.inputs:scriptPath", os.path.join(extension_data_path, "delete_box.py")),
                                                ("delete_box_node.inputs:graph_path", f"/action_graph_{count}")
                                            ],
                                            keys.CONNECT: [
                                                ("on_playback_tick.outputs:tick", "script_node.inputs:execIn"),
                                                ("on_stage_event.outputs:execOut", "delete_box_node.inputs:execIn")
                                            ]
                                        }
                                    )



                        print(f"{image_name[:-4]} num: {count}")


                with ui.HStack():
                    ui.Button("Add", clicked_fn=on_click)

    def on_shutdown(self):
        print("[add_payloads] add_payloads shutdown")

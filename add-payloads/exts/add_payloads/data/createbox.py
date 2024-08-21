import omni.kit.commands
import os
from pxr import Sdf, Usd
import time

def setup(db: og.Database):
    state = db.per_instance_state
    state.count = 1
    state.last_time = time.time()
    state.manager = omni.kit.app.get_app().get_extension_manager()
    state.extionsion_data_path = os.path.join(state.manager.get_extension_path_by_module("add_payloads"), "data")
    state.box_path_list = []

def cleanup(db: og.Database):
    pass

def compute(db: og.Database):
    state = db.per_instance_state
    index = db.inputs.index

    if time.time() - state.last_time > 5:
        prim_path = f"/World/cardbox_{index}_{str(state.count).zfill(2)}"
        state.box_path_list.append(prim_path)

        omni.kit.commands.execute('CreatePayload',
            usd_context=omni.usd.get_context(),
            path_to=prim_path,
            asset_path=os.path.join(state.extionsion_data_path, "cardbox.usd"),
            instanceable=False)

        x = db.inputs.location[0]
        y = db.inputs.location[1]
        z = 350.0

        omni.kit.commands.execute('TransformMultiPrimsSRTCpp',
            count=1,
            paths=[prim_path],
            new_translations=[x, y, z],
            # new_translations=[0.0, 0.0, 0.0],
            new_rotation_eulers=[0.0, -0.0, 0.0],
            new_rotation_orders=[0, 1, 2],
            new_scales=[100, 100, 100],
            old_translations=[0.0, 0.0, 0.0],
            old_rotation_eulers=[0.0, -0.0, 0.0],
            old_rotation_orders=[0, 1, 2],
            old_scales=[1.0, 1.0, 1.0],
            usd_context_name='',
            time_code=0.0)

        state.count += 1
        state.last_time = time.time()

    return True

# This script is executed the first time the script node computes, or the next time
# it computes after this script is modified or the 'Reset' button is pressed.
#
# The following callback functions may be defined in this script:
#     setup(db): Called immediately after this script is executed
#     compute(db): Called every time the node computes (should always be defined)
#     cleanup(db): Called when the node is deleted or the reset button is pressed
# Available variables:
#    db: og.Database The node interface - attributes are exposed in a namespace like db.inputs.foo and db.outputs.bar.
#                    Use db.log_error, db.log_warning to report problems in the compute function.
#    og: The omni.graph.core module
import omni.kit.commands
import os
from pxr import Sdf, Usd
import time


def setup(db: og.Database):
    state = db.per_instance_state
    state.box_path_list = []
    state.count = 1
    state.last_time = time.time()
    state.manager = omni.kit.app.get_app().get_extension_manager()
    state.extension_data_path = os.path.join(state.manager.get_extension_path_by_module("refined_create_box"), "data")


def cleanup(db: og.Database):
    pass


def compute(db: og.Database):
    state = db.per_instance_state
    index = db.inputs.index

    if time.time() - state.last_time > 5:
        prim_path = f'/World/cardbox_{index}_{str(state.count).zfill(2)}'
        state.box_path_list.append(prim_path)

        omni.kit.commands.execute('CreatePayload',
            usd_context=omni.usd.get_context(),
            path_to=prim_path,
            asset_path=os.path.join(state.extension_data_path, 'cardbox.usd'),
            instanceable=False)

        x = db.inputs.location[0]
        y = db.inputs.location[1]
        z = 210.0

        omni.kit.commands.execute('TransformMultiPrimsSRTCpp',
            count=1,
            paths=[prim_path],
            new_translations=[x, y, z],
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
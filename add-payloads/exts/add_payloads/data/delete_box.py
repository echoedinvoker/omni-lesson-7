import omni.kit.commands
import os
from pxr import Sdf, Usd
import time

def setup(db: og.Database):
    pass

def cleanup(db: og.Database):
    pass

def compute(db: og.Database):
    node = og.get_node_by_path(f"{db.inputs.graph_path}/script_node")
    state = db.per_instance_internal_state(node)

    for box_path in state.box_path_list:
        omni.kit.commands.execute('DeletePrims',
            paths=[Sdf.Path(box_path)],
            destructive=False)

    return True

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
    pass


def cleanup(db: og.Database):
    pass


def compute(db: og.Database):
    node = og.get_node_by_path(f"{db.inputs.graph_path}/create_box_node")
    state = db.per_instance_internal_state(node)
    state.count = 1

    for box_path in state.box_path_list:
        omni.kit.commands.execute('DeletePrims',
            paths=[Sdf.Path(box_path)],
            destructive=False)

    return True
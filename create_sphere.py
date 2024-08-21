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
import asyncio

async def create_sphere(state):
    while state.flag:
        omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',
            prim_type='Sphere',
            above_ground=True)
        await asyncio.sleep(5)
    state.is_complete = True
     

def setup(db: og.Database):
    state = db.per_instance_state
    state.is_complete = True


def cleanup(db: og.Database):
    state = db.per_instance_state
    state.flag = False


def compute(db: og.Database):
    state = db.per_instance_state
    if state.is_complete:
        state.flag = True
        state.is_complete = False
        asyncio.ensure_future(create_sphere(state))
    return True
from subprocess import check_call
import numpy as np
from functools import partial
import bpy
bl_info = {
    "name": "max color picker",
    "author": "1C0D",
    "version": (1, 0, 1),
    "blender": (2, 93, 0),
    "location": "on a property color",
    "description": "ctrl+E on a color",
    "category": "Interface",
}


try:
    from pynput import mouse
except ImportError:
    pybin = bpy.app.binary_path_python
    check_call([pybin, '-m', 'pip', 'install', 'pynput'])
    from pynput import mouse

try:
    from PIL import Image, ImageGrab
except ImportError:
    pybin = bpy.app.binary_path_python
    check_call([pybin, '-m', 'pip', 'install', 'pillow'])
    from PIL import Image, ImageGrab


def to_srgb(a):
    gamma = 2.237 #log(0.27,142/255)
    b = ((a / 255) ** gamma)

    return b

def checkColor(x, y):
    zone = 1
    bbox = (x, y, x+zone, y+zone)
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
    im = ImageGrab.grab(bbox=bbox)
    rgb = im.convert('RGB')
    tot = list(rgb.getpixel((0, 0)))
    print('tot', tot)

    for i,e in enumerate(tot):
        tot[i]=to_srgb(e)
    tot.append(1)
    
    
    exec(f'{value} = {tot}')


def on_click(x, y, button, pressed):

    if pressed:
        try:
            checkColor(x, y)
        except Exception as e:
            print(e)

    else:
        # Stop listener
        return False


# def on_scroll(x, y, dx, dy):
    # print('Scrolled {0}'.format((x, y)))


class Max_OT_eye_dropper(bpy.types.Operator):
    bl_idname = "max.eye_dropper"
    bl_label = "max eye dropper"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.ui.copy_data_path_button.poll()  

    def execute(self, context):

        bpy.ops.ui.copy_data_path_button(full_path=True)
        global value
        value = bpy.context.window_manager.clipboard

        bpy.context.window.cursor_set("EYEDROPPER")

        # Collect events until released
        with mouse.Listener(
                on_click=on_click,
                # on_scroll=on_scroll,
                ) as listener:
            listener.join()
        bpy.context.window.cursor_set("DEFAULT")
        return {'FINISHED'}


addon_keymaps = []
classes = (Max_OT_eye_dropper, )


def register():

    for c in classes:
        bpy.utils.register_class(c)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name='User Interface', space_type='EMPTY')

        kmi = km.keymap_items.new('max.eye_dropper', 'E', 'PRESS', ctrl=True)

        addon_keymaps.append((km, kmi))


def unregister():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()

    for c in classes:
        bpy.utils.unregister_class(c)

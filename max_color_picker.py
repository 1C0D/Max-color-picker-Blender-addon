from subprocess import check_call
import numpy as np
import bpy
bl_info = {
    "name": "max color picker",
    "author": "1C0D",
    "version": (1, 0, 0),
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


def checkColor(x, y):
    zone = 2  # 4 pixels
    bbox = (x, y, x+zone, y+zone)
    im = ImageGrab.grab(bbox=bbox)
    rgba = im.convert('RGBA')
    tot = []
    for i in range(zone):
        for j in range(zone):
            tot.append(list(rgba.getpixel((i, j))))
    tot = np.array(tot)
    global res
    res = list(np.sum(tot, 0)/(zone*2)/255)


def on_click(x, y, button, pressed):

    if pressed:
        checkColor(x, y)

    else:
        print('finished!!')
        # Stop listener
        return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0}'.format((x, y)))


class Max_OT_eye_dropper(bpy.types.Operator):
    bl_idname = "max.eye_dropper"
    bl_label = "max eye dropper"

    def execute(self, context):

        bpy.ops.ui.copy_data_path_button(full_path=True)
        value = bpy.context.window_manager.clipboard
        print("value0", value)  # Dbg
        bpy.context.window.cursor_set("EYEDROPPER")

        # Collect events until released
        with mouse.Listener(
                on_click=on_click,
                on_scroll=on_scroll) as listener:
            listener.join()

        exec(f'{value} = {res}')
        print("value", value)  # Dbg
        print("res", res)  # Dbg

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

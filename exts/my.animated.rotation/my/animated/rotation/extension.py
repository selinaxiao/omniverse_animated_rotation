import omni.ext
import omni.ui as ui
import omni.kit.commands
from pxr import Gf, Sdf, Usd
from omni.anim.curve_editor import SingletonCurveEditor
import omni.kit.widget.timeline.scripts.ui_helpers
# from omni.anim.curve_editor.curve_editor_view import CurveEditorView
# from omni.anim.curve_editor import CurveEditorExtension


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[my.animated.rotation] MyExtension startup")
        self._ext_id = ext_id
        self.prev_interval = 0
        self.prev_num_of_intervals = 0
        self.prev_prims = []
        self.prev_prim_path = []

        self._window = ui.Window("Animated Rotation", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                with ui.HStack():
                    ui.Label("Frame Interval")
                    self.field1 = ui.StringField(tooltip = "Seconds in integer")
                ui.Spacer()
                with ui.HStack():
                    ui.Label("Number of Frames")
                    self.field2 = ui.StringField(tooltip = "Integer")
                ui.Spacer()
                with ui.HStack():
                    ui.Label("Horizontal Rotation Angle")
                    self.field3 = ui.StringField(tooltip = "Degrees")
                ui.Spacer()
                with ui.HStack():
                    ui.Label("Vertical Rotation Angle")
                    self.field4 = ui.StringField(tooltip = "Degrees")
                ui.Spacer()
                ui.Button("rotate start", clicked_fn=lambda: self.on_click())

    def on_click(self):
        self.clean_up()
    
        time_interval = self.field1.model.get_value_as_int()
        number_of_interval = self.field2.model.get_value_as_int()
        h_angle = self.field3.model.get_value_as_float()
        v_angle = self.field4.model.get_value_as_float()

        # print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        
        self.prev_interval = time_interval
        self.prev_num_of_intervals = number_of_interval
        prims = self.get_prims()
        if prims:
            print(h_angle, v_angle)
            for i in range(len(prims)):
                current_prim = prims[i].GetAttribute('xformOp:rotateXYZ').Get()
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ'),
                    value=Gf.Vec3d(0.0,0.0,0.0),
                    prev=current_prim)

            omni.kit.commands.execute('SetAnimCurveKey', time=Usd.TimeCode(0),
                paths=[str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|x', str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|y', str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|z'])
        

            for j in range(number_of_interval+1):
                time = (j+1)* time_interval
                omni.kit.commands.execute('ChangeProperty',
                    prop_path=Sdf.Path(str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ'),
                    value=Gf.Vec3d((current_prim[0]+h_angle*(j+1)), current_prim[1], (current_prim[2]+v_angle*(j+1))),
                    prev=current_prim)

                omni.kit.commands.execute('SetAnimCurveKey', time=Usd.TimeCode(time),
                paths=[str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|x', str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|y', str(prims[i].GetPrimPath())+'.xformOp:rotateXYZ|z'])
        self.prev_prims = prims


    def on_shutdown(self):
        print("[my.animated.rotation] MyExtension shutdown")



    """helper functions"""

    # remove all the key frames from previous start
    def clean_up(self):
        self.prev_prim_path = []
        self.prev_path_rotation = []
        self.prev_rotation = []
        for i in range(len(self.prev_prims)):
            self.prev_prim_path.append(str(self.prev_prims[i].GetPrimPath()))
            self.prev_path_rotation.append(str(self.prev_prims[i].GetPrimPath())+'animationData.xformOp:rotateXYZ:x')
            self.prev_path_rotation.append(str(self.prev_prims[i].GetPrimPath())+'animationData.xformOp:rotateXYZ:z')
            self.prev_rotation.append((str(self.prev_prims[i].GetPrimPath())+'.xformOp:rotateXYZ:x'))
            self.prev_rotation.append((str(self.prev_prims[i].GetPrimPath())+'.xformOp:rotateXYZ:y'))
            self.prev_rotation.append((str(self.prev_prims[i].GetPrimPath())+'.xformOp:rotateXYZ:z'))
        # print([t for t in range(0, self.prev_interval*self.prev_num_of_intervals, self.prev_num_of_intervals)])
        print("-------------------------------")
        print([a for a in self.prev_path_rotation for n in range(self.prev_num_of_intervals)])
        print("-------------------------------")
        print([b for b in self.prev_prim_path for m in range(self.prev_num_of_intervals*2)])
        print("-------------------------------")
        print(SingletonCurveEditor.get_instance_ref())

        
        context = omni.usd.get_context()
        stage = context.get_stage()

        if (self.prev_num_of_intervals != 0):
            delete_times=[t for t in range(self.prev_interval, self.prev_interval*self.prev_num_of_intervals+1, self.prev_interval)]
            delete_track_names=[a for a in self.prev_path_rotation for n in range(self.prev_num_of_intervals)]
            delete_track_users=[b for b in self.prev_prim_path for m in range(self.prev_num_of_intervals*2)]
            
            print("-------------------------------")
            print(delete_times)
            print("-------------------------------")
            print(delete_track_users)

            omni.kit.commands.execute('ChangeSelectionCurveCommand',
            new_times=[],
            new_track_names=[],
            new_track_users=[],
            delete_times=delete_times,
            delete_track_names=delete_track_names,
            delete_track_users=delete_track_users,
            singleton_curve_editor_wp=SingletonCurveEditor.get_instance_ref(),
            edit_scope=omni.kit.widget.timeline.scripts.ui_helpers.EditScope())

            root_layer = stage.GetRootLayer()
            session_layer = stage.GetSessionLayer()
            print(root_layer)

            for keys in range(len(delete_times)):
                print(delete_times[keys])
                
                omni.kit.commands.execute('RemoveAnimCurveKey',
                    stage=Usd.Stage.Open(rootLayer=root_layer, sessionLayer=session_layer),
                    paths=[self.prev_rotation[0]],
                    time=Usd.TimeCode(delete_times[keys]))

                
                omni.kit.commands.execute('RemoveAnimCurveKey',
                    stage=Usd.Stage.Open(rootLayer=root_layer, sessionLayer=session_layer),
                    paths=[self.prev_rotation[2]],
                    time=Usd.TimeCode(delete_times[keys]))
                
                omni.kit.commands.execute('RemoveAnimCurveKey',
                    stage=Usd.Stage.Open(rootLayer=root_layer, sessionLayer=session_layer),
                    paths=[self.prev_rotation[1]],
                    time=Usd.TimeCode(delete_times[keys]))

    def get_prims(self):
        context = omni.usd.get_context()
        stage = context.get_stage()
        prims = [stage.GetPrimAtPath(m) for m in context.get_selection().get_selected_prim_paths()]
        return prims


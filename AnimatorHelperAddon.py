import bpy
import mathutils
import math
bl_info = {
    "name": "Animator Helper",
    "description": "Transforming tool for animacions",
    "author": "Nori_SC",
    "location": "View3D > Panel",
    "blender": (2, 80, 0),
    "category": "Animation",
}
def GetBones():
    active_pose_bone = bpy.context.active_pose_bone
    pose_bones = bpy.context.selected_pose_bones
    i = -1;
    for pose_bone in pose_bones:
        i = i+1
        if pose_bone == active_pose_bone:
            del pose_bones[i]
            pose_bones.insert(0,active_pose_bone)
            return pose_bones
def MirorMatrix(matrix):
    loc, rot, sca = matrix.decompose()
    loc[0] = -loc[0]
    rot[0] = rot[0] * -1
    rot[1] = rot[1] * -1
    newmatrix = MakeMatrix(loc, rot, sca)
    return newmatrix
    
def MakeMatrix(loc, rot, sca):
    mat_loc = mathutils.Matrix.Translation(loc)
    mat_sca = mathutils.Matrix.Scale(1, 4, sca)
    mat_rot = rot.to_matrix().to_4x4()
    mat_out = mat_loc @ mat_rot @ mat_sca
    return mat_out
    
class TransformPanel(bpy.types.Panel):
    bl_label = "Transform"
    bl_idname = "PT_MoveToTarget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AnimatorHelper'
    @classmethod
    def poll(cls, context):
        return context.mode in {'POSE'}
    def draw(self, context):
        if bpy.context.object is not None:
            

            layout = self.layout
            #print(arma_items[])
            scene = context.scene
                
            col = layout.column()
            
            col.prop_search(scene, "object_name", bpy.data, "objects")
            
            if bpy.context.object.type == 'ARMATURE' and context.scene.object_name is not "":
                if len(bpy.context.selected_pose_bones) is not 0:
                    if len(bpy.context.selected_pose_bones) is 2:
                        col_03 = layout.column()
                        col_03.operator("pose.swap_bone_rotacion", icon= 'CON_LOCLIKE')
                        col_03.operator("pose.swap_bone_location", icon= 'CON_LOCLIKE')
                        col_03.operator("pose.swap_bone_transform", icon= 'CON_LOCLIKE')
                        col_03.operator("pose.miror_bone_transform", icon= 'CON_LOCLIKE')
                        
                        layout.label(text="From: " + GetBones()[0].name +" To: "+ GetBones()[1].name)
                    else:
                        layout.label(text="Selected Bone: " + bpy.context.selected_pose_bones[0].name)
                        if len(bpy.context.selected_pose_bones) is 1:
                            row_01 = layout.row()
                            row_01.operator("pose.move_to_target", icon= 'CON_LOCLIKE')
                            row_01.prop(scene, "use_bone_location_offset",text="")
                            if scene.use_bone_location_offset == True:
                                col_01 = layout.column()
                                col_01.prop(scene, "bone_location_offset")
                            
                            row_02 = layout.row()
                            row_02.operator("pose.rotate_to_target", icon= 'CON_ROTLIKE')
                            row_02.prop(scene, "use_bone_rotacion_offset",text="")
                            if scene.use_bone_rotacion_offset == True:
                                col_02 = layout.column()
                                col_02.prop(scene, "bone_rotacion_offset")
                    
                    
                    
                else:
                    layout.label(text="Selected Bone: None")
#---------------------------------------------------------------------------------------------------------
class _PT_MoveToTarget(bpy.types.Operator):
    bl_idname = "pose.move_to_target"
    bl_label = "Move To Target"
    def execute(self,context):
        armature = bpy.context.object
            
        Target = bpy.data.objects.get(context.scene.object_name)
        pb = bpy.context.selected_pose_bones[0]
        #getMatrix
        obj = pb.id_data
        BoneWorldMatrix = obj.matrix_world @ pb.matrix
        #SnapToTarget
        if bpy.context.scene.use_bone_location_offset == True:
           BoneWorldMatrix.translation = Target.matrix_world.translation + bpy.context.scene.bone_location_offset
        else:
            BoneWorldMatrix.translation = Target.matrix_world.translation
        pb.matrix = armature.convert_space(pose_bone=pb, 
        matrix=BoneWorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        return {"FINISHED"}
    
#---------------------------------------------------------------------------------------------------------
class _PT_RotateToTarget(bpy.types.Operator):
    bl_idname = "pose.rotate_to_target"
    bl_label = "Rotate To Target"
    def execute(self,context):
        armature = bpy.context.object
            
        Target = bpy.data.objects.get(context.scene.object_name)
        pb = bpy.context.selected_pose_bones[0]
        #getMatrix
        obj = pb.id_data
        BoneWorldMatrix = obj.matrix_world @ pb.matrix
        #rotate to target keep location
        WorldEuler = Target.matrix_world.to_euler().to_matrix().to_4x4()
        WorldEuler.translation = BoneWorldMatrix.translation
        
        Test = armature.convert_space(pose_bone=pb, 
        matrix=WorldEuler, 
        from_space='WORLD', 
        to_space='POSE')
        
        if bpy.context.scene.use_bone_rotacion_offset == True:
            pb.matrix = Test @ bpy.context.scene.bone_rotacion_offset.to_matrix().to_4x4()
        else:
            pb.matrix = Test
        return {"FINISHED"}
class _PT_SwapBoneRotacion(bpy.types.Operator):
    bl_idname = "pose.swap_bone_rotacion"
    bl_label = "Swap Bone Rotacion"
    def execute(self,context):
        armature = bpy.context.object
            
        pb = GetBones()[0]
        pb1 = GetBones()[1]
        #getMatrix
        obj = pb.id_data
        obj1 = pb1.id_data
        Bone1WorldMatrix = obj.matrix_world @ pb.matrix
        Bone2WorldMatrix = obj1.matrix_world @ pb1.matrix
        #rotate to target keep location
        WorldEuler = Bone2WorldMatrix.to_euler().to_matrix().to_4x4()
        WorldEuler.translation = Bone1WorldMatrix.translation
        
        Test = armature.convert_space(pose_bone=pb, 
        matrix=WorldEuler, 
        from_space='WORLD', 
        to_space='POSE')
        
        pb.matrix = Test
        
        WorldEuler = Bone1WorldMatrix.to_euler().to_matrix().to_4x4()
        WorldEuler.translation = Bone2WorldMatrix.translation
        
        Test = armature.convert_space(pose_bone=pb, 
        matrix=WorldEuler, 
        from_space='WORLD', 
        to_space='POSE')
        
        pb1.matrix = Test

        return {"FINISHED"}
class _PT_SwapBoneLocation(bpy.types.Operator):
    bl_idname = "pose.swap_bone_location"
    bl_label = "Swap Bone Location"
    def execute(self,context):
        armature = bpy.context.object
            
        pb = GetBones()[0]
        pb1 = GetBones()[1]
        #getMatrix
        obj = pb.id_data
        obj1 = pb.id_data
        Bone1WorldMatrix = obj.matrix_world @ pb.matrix
        Bone2WorldMatrix = obj1.matrix_world @ pb1.matrix
        #rotate to target keep location
        backupBone1WorldMatrix = Bone1WorldMatrix.copy()
        backupBone2WorldMatrix = Bone2WorldMatrix.copy()
        
        Bone1WorldMatrix.translation = backupBone2WorldMatrix.translation
        Bone2WorldMatrix.translation = backupBone1WorldMatrix.translation
        
        Test1 = armature.convert_space(pose_bone=pb, 
        matrix=Bone1WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        
        Test2 = armature.convert_space(pose_bone=pb1, 
        matrix=Bone2WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        
        pb.matrix = Test1
        pb1.matrix = Test2

        return {"FINISHED"}
    
class _PT_SwapBoneTransform(bpy.types.Operator):
    bl_idname = "pose.swap_bone_transform"
    bl_label = "Swap Bone Transform"
    def execute(self,context):
        armature = bpy.context.object
            
        pb = GetBones()[0]
        pb1 = GetBones()[1]
        #getMatrix
        obj = pb.id_data
        obj1 = pb.id_data
        Bone1WorldMatrix = obj.matrix_world @ pb.matrix
        Bone2WorldMatrix = obj1.matrix_world @ pb1.matrix
        #rotate to target keep location
        
        
        Test1 = armature.convert_space(pose_bone=pb, 
        matrix=Bone1WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        Test2 = armature.convert_space(pose_bone=pb1, 
        matrix=Bone2WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        
        pb.matrix = Test2
        pb1.matrix = Test1

        return {"FINISHED"}
class _PT_MirorBoneTransform(bpy.types.Operator):
    bl_idname = "pose.miror_bone_transform"
    bl_label = "Miror Bone Transform"
    def execute(self,context):
        armature = bpy.context.object
        
        pb = GetBones()[0]
        pb1 = GetBones()[1]
        #getMatrix
        obj = pb.id_data
        obj1 = pb.id_data
        Bone1WorldMatrix = obj.matrix_world @ pb.matrix
        Bone2WorldMatrix = obj1.matrix_world @ pb1.matrix
        Bone1WorldMatrix = MirorMatrix(Bone1WorldMatrix)
        Bone2WorldMatrix = MirorMatrix(Bone2WorldMatrix)
        
        Test2 = armature.convert_space(pose_bone=pb1, 
        matrix=Bone1WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        Test1 = armature.convert_space(pose_bone=pb1, 
        matrix=Bone2WorldMatrix, 
        from_space='WORLD', 
        to_space='POSE')
        
        
        pb1.matrix = Test2
        pb.matrix = Test1
        
        return {"FINISHED"}
#---------------------------------------------------------------------------------------------------------
def arma_items(self, context):
    self.arma_items.clear()
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
    return obs

def arma_upd(self, context):
    self.arma_coll.clear()
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            item = self.arma_coll.add()
            item.name = ob.name

def bone_items(self, context):
    arma = context.scene.objects.get(self.arma)
    if arma is None:
        return
    return [(bone.name, bone.name, "") for bone in arma.data.bones]

def obj_items(self, context):
    objs = context.scene.objects
    if objs is None:
        return
    return [(obj.name, obj.name, "") for obj in objs]
#--------------------------------------Register And Unregister--------------------------------------------

def register():
    bpy.utils.register_class(TransformPanel)
    bpy.utils.register_class(_PT_MoveToTarget)
    bpy.utils.register_class(_PT_RotateToTarget)
    bpy.utils.register_class(_PT_SwapBoneRotacion)
    bpy.utils.register_class(_PT_SwapBoneLocation)
    bpy.utils.register_class(_PT_SwapBoneTransform)
    bpy.utils.register_class(_PT_MirorBoneTransform)
    
    bpy.types.Scene.arma = bpy.props.EnumProperty(items=arma_items, update=arma_upd)
    bpy.types.Scene.bone = bpy.props.EnumProperty(items=bone_items)
    bpy.types.Scene.arma_coll = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    bpy.types.Scene.arma_name = bpy.props.StringProperty(name="Rig")
    
    bpy.types.Scene.bone_location_offset = bpy.props.FloatVectorProperty(name="Offset Location",subtype='XYZ')
    bpy.types.Scene.use_bone_location_offset = bpy.props.BoolProperty(name="Use Offset Location")
    
    bpy.types.Scene.bone_rotacion_offset = bpy.props.FloatVectorProperty(name="Offset Rotacion",subtype='EULER')
    bpy.types.Scene.use_bone_rotacion_offset = bpy.props.BoolProperty(name="Use Offset Rotacion")
    
    bpy.types.Scene.bone_name = bpy.props.StringProperty(name="Bone")
    bpy.types.Scene.object_name = bpy.props.StringProperty(name="Target")

def unregister():
    bpy.utils.unregister_class(TransformPanel)
    bpy.utils.unregister_class(_PT_MoveToTarget)
    bpy.utils.unregister_class(_PT_RotateToTarget)
    bpy.utils.unregister_class(_PT_SwapBoneRotacion)
    bpy.utils.unregister_class(_PT_SwapBoneLocation)
    bpy.utils.unregister_class(_PT_SwapBoneTransform)
    bpy.utils.unregister_class(_PT_MirorBoneTransform)
    
    del bpy.types.Scene.arma
    del bpy.types.Scene.bone
    del bpy.types.Scene.arma_name
    del bpy.types.Scene.bone_name
    del bpy.types.Scene.object_name
    del bpy.types.Scene.arma_coll
    
    del bpy.types.Scene.bone_location_offset
    del bpy.types.Scene.use_bone_location_offset
    
    del bpy.types.Scene.bone_rotacion_offset
    del bpy.types.Scene.use_bone_rotacion_offset

if __name__ == "__main__":
    register()
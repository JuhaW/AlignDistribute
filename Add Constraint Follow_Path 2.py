import bpy
from math import sqrt
from bpy.props import BoolProperty, FloatProperty

_selected_curves = []
bpy.types.Scene.Distribute = BoolProperty(default = True)
bpy.types.Scene.Distance = BoolProperty(default = True)
bpy.types.Scene.Add = FloatProperty(default = .1,min = 0, max = 1)

def get_selection(self):
	curves = [c for c in self.selected_objects if c.type == 'MESH' or c.type == 'CURVE']
	dels = set(_selected_curves) - set(curves)
	if len(dels):
		for c in dels:
			_selected_curves.remove(c)

	for c in curves:
		if c not in _selected_curves:
			_selected_curves.append(c)
	return _selected_curves


bpy.types.Context.selected_curves = property(get_selection)


class HelloWorldPanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_label = "Selected Objects"
	bl_idname = "OBJECT_PT_hello"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		layout.prop(context.scene,"Distribute","Full distribute")
		layout.prop(context.scene,"Distance","Nearest first")
		layout.prop(context.scene,"Add","Offset")
		layout.operator("distribute.meshes")
		obj = context.object
		layout.label("Last selected object")
		layout.label(str(context.selected_curves[-1].name),icon='OUTLINER_DATA_CURVE')
		#layout.label("%d objects selected" % len(context.selected_curves))
		#for curve in context.selected_curves:
		#	row = layout.row()
		#	row.prop(curve, "name", icon='OUTLINER_DATA_CURVE', text="")


#
class OBJECT_OT_Distribute(bpy.types.Operator):
	bl_idname = "distribute.meshes"
	bl_label = "Distribute"

	def execute(self, context):
		obj = context.object
		print ("##############################")
		print ("button pressed")
		print ("##############################")
		# for curve in context.selected_curves:
		# print ("distribute",curve)

		if len(_selected_curves) > 1:
			Do_distribute()

		return {'FINISHED'}


# --------------------------------------
def Do_distribute():
	print ("follow path")
	selected_obj = bpy.context.selected_curves
	context = bpy.context
	obj = context.object
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True

	if obj.type == 'CURVE':
		obj.data.use_radius = False

		print (obj.dimensions)
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		print ("Scale =",obj.scale)
		selection_count = len(selected_obj)

		if selection_count == 2:
			add = 0
		elif context.scene.Distribute:
			add = 1/(selection_count-2 + obj.data.splines[0].use_cyclic_u)
		else:
			#add = 1/(selection_count-1)
			add = context.scene.Add

		posoffset = 0
		# ordermode 0 = selection order
		# ordermode 1 = distance to curve order, nearest first
		#ordermode = context.scene.Distance

		if not context.scene.Distance :

			for x in (selected_obj[:-1]):
				set_follow_path(x,obj,add,posoffset)
				posoffset = posoffset + add
		else:
			dist_table = calculate_distance(selected_obj)

			for x in dist_table:
				obj = bpy.context.object

				set_follow_path(selected_obj[x[0]],obj,add,posoffset)
				posoffset = posoffset + add
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = obj
		obj.select = True
		# bpy.ops.object.location_clear()
	else:
		print("Active object is not curve object")
# --------------------------------------

def set_follow_path(x,obj,add,posoffset):
	#x.parent = obj
	bpy.ops.object.select_all(action='DESELECT')
	bpy.context.scene.objects.active = x
	x.select = True
	x.location = [0,0,0]

	bpy.context.scene.objects.active = obj

	if x.type == 'MESH':
		objs = x.constraints.new(type='FOLLOW_PATH', )
		objs.target = bpy.context.active_object
		objs.use_fixed_location = True
		objs.offset_factor = posoffset

# get distances of selected objects from curve object
def get_distance(l1,curveobj):
	# l2 = [0, 0, 0]
	l2 = curveobj.location
	print ("location:", l2)
	distance = sqrt((l1[0] - l2[0]) ** 2 + (l1[1] - l2[1]) ** 2 + (l1[2] - l2[2]) ** 2)
	return distance


def calculate_distance(selected_obj):
	obj_list = selected_obj[:-1]
	print ("obj_list=",selected_obj)
	dist_table = []
	rowcnt = len(selected_obj[:-1])
	print ("ROWCNT ==========",rowcnt)
	for row in range(rowcnt): dist_table += [[0] * 2]
	cnt = 0

	for item in selected_obj[:-1]:
		a = get_distance(item.location,selected_obj[-1])
		# print ("Distance:", a)
		dist_table[cnt][0] = cnt
		dist_table[cnt][1] = a
		cnt += 1

	# print (dist_table)
	#######################################
	# sort distance table
	dist_table.sort(key=lambda l: l[1])
	# print ("Sorted list:", dist_table)
	#######################################
	# for item in range(0, rowcnt):
	#	print (obj_list[dist_table[item][0]].name)

	return dist_table


# calculate_distance()
# -------------------------------------------------------------------
def register():
	bpy.utils.register_class(HelloWorldPanel)


def unregister():
	bpy.utils.unregister_class(HelloWorldPanel)


if __name__ == "__main__":
	register()

bpy.utils.register_module(__name__)

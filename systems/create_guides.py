
import maya.cmds as cmds
import importlib
import os
from systems.utils import (utils, system_custom_attr) 

# to change:
from systems.utils.WD_lessons_utils import (control_shape, connect_modules)

importlib.reload(connect_modules)
importlib.reload(utils)
importlib.reload(control_shape)
importlib.reload(system_custom_attr)

scale = 1

class Guides_class():
    def __init__(self, accessed_module, side, 
                 to_connect_to, use_existing_attr, orientation, numb_id,
                 neck_dict=None):
        self.module = importlib.import_module(f"systems.modules.{accessed_module}")
        # Reload the module for any updates!
        importlib.reload(self.module)
       
        # [if] statement for "self.create_guide" variable {if == "hand"}
        # else:
        self.unique_id = numb_id
        self.neck_dict = neck_dict
        if "neck_1" in self.module.system:
            print(f"¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬CREATING GUIDES FOR NECKKK")
            print(f"¬¬¬ {self.neck_dict['nck_sys']}")
        #if "neck_1" in accessed_module: 
         #   self.create_guide = self.The_guides(accessed_module, side, use_existing_attr, orientation)
        #else:
        self.create_guide = self.The_guides(accessed_module, side, use_existing_attr, orientation)
    
    def collect_guides(self):
        print("This print is from 'collect_guides() in class'")
        return self.create_guide

    def The_guides(self, accessed_module, side, use_existing_attr, orientation):
        print("This print is from 'The_guides() in class'")
        guide_connector_list = []
        self.system_to_connect = []
        selection = cmds.ls(sl=1)
          
        if not "root_basic" in accessed_module:
            if selection:
                if "master" in selection[0]:
                    print("> CR_guides, can't attatch a new mdl to a master ctrl bruh")
                elif "master" not in selection[0]:
                    guide = self.creation(accessed_module, side, guide_connector_list, use_existing_attr, orientation)
                    master_guide = guide["master_guide"]
                    guide_connector = connect_modules.attach(master_guide, selection)
                    guide_connector_list.append(guide_connector[1])

                    # If the module is finger, match the master guide to the selected guide
                    if 'finger' in master_guide or 'neck' in master_guide:
                        cmds.matchTransform(master_guide, selection, pos=1, rot=1, scl=0)
                    
                    # Calling WD ".prep_attach_jnts" is designed to prepare and organize 
                    # joint relationships in the context of creating blueprint guides.
                    self.system_to_connect = connect_modules.prep_attach_jnts(master_guide, selection, need_child=True)
                    guide.update({"system_to_connect": self.system_to_connect})
                    return guide
           
        else:
            print(">> Recognised this module is root_basic!")
            guide = self.creation(accessed_module, side, guide_connector_list, use_existing_attr, orientation)
            guide.update({"system_to_connect": []})
            return guide
        
    def creation(self, accessed_module, side, guide_connector_list, use_existing_attr, orientation):
        print(f"CR_GDS side :: {side}")
        print("IN CREATION FUNC, THE ORIENTATION ARG IS: ", orientation)
        
        # 1) Setup & initialisation
        # > Defining file paths & configurations > importing guide shape
        GUIDE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "imports","guide_shape.abc")
        ROOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "imports", "ctrl_root_octagon_import.abc")
       # print("down here")
        #imported = cmds.file(ROOT_FILE, i=1, rnn=1)
        
        guide_list = []
        root_exists = False
        # guide_pref = f"guide_{number_id}"
        
        # 2) Determine Side
        if side == "None":
            side = ""

        ''' If `side` = _R change the pos/rot dict accordingly. '''

        # Orientation:
        if self.module.has_orientation == "None": # root_basic          
            pos_dict = self.module.system_pos
            rot_dict = self.module.system_rot
        else:
            if orientation == "XYZ":
                print("ORIENTATION IS 'xyz' ###")
                if "neck_1" in self.module.system:
                    pos_dict = self.neck_dict["nck_pos_xyz"]
                    rot_dict = self.neck_dict["nck_rot_xyz"]
                else:
                    pos_dict = self.module.system_pos_xyz
                    rot_dict = self.module.system_rot_xyz
            elif orientation == "YZX":
                print("ORIENTATION IS 'yzx' ###")
                if "neck_1" in self.module.system:
                    pos_dict = self.neck_dict["nck_pos_yzx"]
                    rot_dict = self.neck_dict["nck_rot_yzx"]
                else:
                    pos_dict = self.module.system_pos_yzx
                    rot_dict = self.module.system_rot_yzx

        tmp_list = []
        module_list = cmds.ls("data*")
        for obj in module_list:
            if "Shape" in obj:
                pass
            elif accessed_module in obj:
                tmp_list.append(obj)
            elif accessed_module == "root_basic" and "root" in obj:
                tmp_list.append(obj)
        
        # 4) Create master guide for module by looking in each module's variable's
        if "root" in self.module.system:
            master_guide = "root"
        else:
            master_guide = f"master_{self.unique_id}_{accessed_module}{side}"
            control_shape.controlTypes(f"master_{self.unique_id}_{accessed_module}{side}", "octagon")
            print("hmmmm: ", master_guide)
            cmds.setAttr(f"{master_guide}.overrideEnabled", 1)
            cmds.setAttr(f"{master_guide}.overrideColor", 9)
            cmds.scale(8, 8, 8, master_guide)
            #cmds.makeIdentity(master_guide, t=0, r=0, s=1)
            
            # Position the new master guide
            pos = pos_dict[self.module.system[0]]
            rot = rot_dict[self.module.system[0]]
            cmds.xform(master_guide, ws=1, t=[pos[0], pos[1], pos[2]])
            cmds.xform(master_guide, ws=1, ro=[rot[0], rot[1], rot[2]])
            
        # 5) Guide creation loop
        if "neck_1" in self.module.system:
            print(f"$$$$$$$$$$$$$ Cr_Guides > {self.neck_dict['nck_sys']}")
            system_module = self.neck_dict["nck_sys"]
        else:
            system_module = self.module.system

        for x in system_module:
          #  try: 
            if "root" in x:
                imported = cmds.file(ROOT_FILE, i=1, rnn=1)
                cmds.scale(self.module.guide_scale, self.module.guide_scale, 
                            self.module.guide_scale, imported)
                print(">>>>>>>>root print in creation()")
                root_exists = True
                
                guide = cmds.rename(imported[0], f"guide_{self.unique_id}_{x}")
                print(f"root guide: {guide}")
                utils.colour_root_control(guide)
            else:
                imported = cmds.file(GUIDE_FILE, i=1, namespace="guide_shape_import", rnn=1)
                cmds.scale(self.module.guide_scale+0.5, self.module.guide_scale+0.5, 
                            self.module.guide_scale+0.5, imported)
                guide = cmds.rename(imported[0], f"guide_{self.unique_id}_{x}{side}")
                utils.colour_guide_custom_shape(guide)
            
            if "root" in x and root_exists is True:
                master_guide = guide
            #elif "biped_phal_proximal" in system_module:
            #    master_guide = guide
            else:
                print("print else <<<<<")
                guide_list.append(guide)
            
            # Use the selected dict's to set location and rotation
            pos = pos_dict[x]
            rot = rot_dict[x]
            cmds.xform(guide, ws=1, t=[pos[0], pos[1], pos[2]])
            cmds.xform(guide, ws=1, ro=[rot[0], rot[1], rot[2]])
            
            # Add a custom attr to each guide to specify its original type
            cmds.addAttr(guide, ln="original_guide", at="enum", en=x, k=0)

        # 6) Parenting & connecting guides
        guide_list.reverse()
        ui_guide_list = guide_list
        guide_list.append(master_guide)
        #print("1: ", guide_list)
        #print("2: ", len(guide_list))
        
        print(f"CONNECTING GUIDES create_guides: {guide_list}")
        for i in range(len(guide_list)):
            try:
                cmds.parent(guide_list[i], guide_list[i+1])
                guide_connector = utils.guide_curve_connector(guide_list[i], guide_list[i+1])
                guide_connector_list.append(guide_connector)
            except:
                pass # ignore last element of the list erroring.

        # Guide connectors are grouped under this grp: 
        if "grp_guideConnector_clusters" in cmds.ls("grp_guideConnector_clusters"):
            cmds.parent(guide_connector_list, "grp_guideConnector_clusters")
        else: 
            cmds.group(guide_connector_list, n="grp_guideConnector_clusters", w=1)
        cmds.select(cl=1)
        
        #----------------------------------------------------------------------
        # Create  data guide
        if "root" in system_module: # or "proximal" in self.module.system:
            data_guide_name = f"data_{master_guide}"
        else:
            print("ERRRRRRRRRRRRRRRRRRRRRRRROOOOOOOR: ", master_guide)
            data_guide_name = master_guide.replace("master_", f"data_")
        cmds.group(n=data_guide_name, em=1)
        #cmds.spaceLocator(n=data_guide_name)
        cmds.matchTransform(data_guide_name, master_guide)
        cmds.parent(data_guide_name, master_guide)
        cmds.setAttr(f"{data_guide_name}.visibility", 0)
        #----------------------------------------------------------------------

        # 7) Add attributes
        self.available_rig_modules_type = ":".join(self.module.available_rig_types) 
        # self.module.available_rig_types is the variable found within each module, arm, leg & so on. 
        # In this case it's getting the '["IK", "FK", "IKFK"]' varible for the custom attribiutes!
        
        # custom_attribute = self.add_custom_attr(guide_list, master_guide, use_existing_attr, accessed_module)
        system_custom_attr.buildCustomAttr(guide_list, master_guide, use_existing_attr, accessed_module, self.available_rig_modules_type)
        
        cmds.addAttr(master_guide, ln="is_master", at="enum", en="True", k=0)
        cmds.addAttr(master_guide, ln="base_module", at="enum", en=accessed_module, k=0) # mdl_attr
        cmds.addAttr(master_guide, ln="module_side", at="enum", en=side, k=0)
        cmds.addAttr(master_guide, ln="master_guide", at="enum", en=master_guide, k=0)
        cmds.addAttr(master_guide, ln="module_orientation", at="enum", en=orientation, k=0)
        # Adding the proxy 
        for item in ["is_master", "base_module", "module_side", "master_guide", "module_orientation"]:
            cmds.addAttr(guide_list[:-1],ln=f"{item}", proxy=f"{guide_list[-1]}.{item}")
            for guide in guide_list[:-1]:
                cmds.setAttr(f"{guide}.{item}",k=0)
        
        # 9) Return UI data
        # Return a dictionary containing master_guide, guide_connector_list & 
        # ui_guide_list for further use in the ui
        ui_dict = {
            "master_guide": master_guide, 
            "guide_connector_list": guide_connector_list,
            "ui_guide_list": ui_guide_list, 
            "data_guide": data_guide_name,
            "guide_number": self.unique_id
        }
        return ui_dict


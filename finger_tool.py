from __future__ import print_function
import pythonidelib
from pyfbsdk import *
from pyfbsdk_additions import *
from PySide import QtGui, QtCore, QtUiTools, shiboken

#CONSTANTS
NAME = 'Finger Controls'
DEVELOPMENT = True
UI_FILE_PATH = r'K:\Staff\USERS\afischer\FINGER_TOOL/finger.ui'

#PYSIDE UI
class NativeWidgetHolder(FBWidgetHolder):
    """
    The FBWidgetHolder that wraps our PyQt/PySide Widget
    """
    def WidgetCreate(self, pWidgetParent):
        
        self.window = None
        
        # Load the UI here and run connections within the FBWidgetHolder
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(UI_FILE_PATH)
        ui_file.open(QtCore.QFile.ReadWrite)
        self.window = loader.load(ui_file, parent=shiboken.wrapInstance(pWidgetParent, QtGui.QWidget))
        ui_file.close
        
        # Connect signals and slots
        try:
            self.create_bone_lists()
            self.make_signal_slots_connections()
        except AttributeError:
            print('Could not bind all signals and slots. Tool might not perform as expected.')
            pythonidelib.FlushOutput()

        return shiboken.getCppPointer(self.window)[0]
        
    def make_signal_slots_connections(self):
        
        self.window.action_close.triggered.connect(self.remove_window_clicked)
        #self.window.hand_check.stateChanged.connect(self.handle_listen)
        
        try:
            for bone in self.HandBoneList:
                if bone.Name == "LeftHand":
                    boneName = "LeftHand"
                    self.window.LeftHand_x.valueChanged.connect(lambda x: self.left_hand(boneName))
                    self.window.LeftHand_y.valueChanged.connect(lambda x: self.left_hand(boneName))
                    self.window.LeftHand_z.valueChanged.connect(lambda x: self.left_hand(boneName))
        except:
            print ("no bones found")
            pass
                
    def left_hand(self, boneName):
        for bone in self.HandBoneList:
            if bone.Name == "LeftHand":
                joint = bone
        if joint in self.intDict:
            intList = self.intDict.get(joint)
            for funcBox in intList:
                if " 3" in funcBox.Name:
                    value = self.window.LeftHand_x.value()
                    IntegerXNode = find_animation_node(funcBox.AnimationNodeInGet(), 'a')
                    #currentValue = IntegerXNode.ReadData()
                    IntegerXNode.WriteData([value])
                if " 4" in funcBox.Name:
                    value = self.window.LeftHand_y.value()
                    IntegerYNode = find_animation_node(funcBox.AnimationNodeInGet(), 'a')
                    IntegerYNode.WriteData([value])
                if " 5" in funcBox.Name:
                    value = self.window.LeftHand_z.value()
                    IntegerZNode = find_animation_node(funcBox.AnimationNodeInGet(), 'a')
                    IntegerZNode.WriteData([value])
        
    def remove_window_clicked(self):
        FBDestroyToolByName(NAME)
        
              
    #Store left and right hand bones in individual lists 
    #Create constraint setup for every bone
    #Create FingerToolFolder. If it already exists, do nothing
    def create_bone_lists(self):
        
        self.HandBoneList = []
        rightHand = FBFindModelByLabelName('_1:Solving:RightHand')
        leftHand = FBFindModelByLabelName('_1:Solving:LeftHand')
        self.HandBoneList.append(rightHand)
        self.HandBoneList.append(leftHand)       
        store_children(rightHand, self.HandBoneList)
        store_children(leftHand, self.HandBoneList)
        
        folderExists = False
        folderComponents = [ component for component in FBSystem().Scene.Components if type(component) == FBFolder ]
        for folder in folderComponents:
            if "FingerToolFolder" == folder.Name:
                folderExists = True
        
        folderSwitch = False
        self.intDict = {}
        try:
            for bone in self.HandBoneList:
                if folderExists == False:
                    integerBoxList = []
                    lConstraintRelation = FBConstraintRelation(bone.Name)
                    lConstraintRelation.Active = True
                    senderBox = lConstraintRelation.SetAsSource(bone)
                    vectorToNumberBox = lConstraintRelation.CreateFunctionBox('Converters', 'Vector to Number')
                    IntegerXBox = lConstraintRelation.CreateFunctionBox('Number', 'Integer')
                    IntegerYBox = lConstraintRelation.CreateFunctionBox('Number', 'Integer')
                    IntegerZBox = lConstraintRelation.CreateFunctionBox('Number', 'Integer')
                    integerBoxList.append(IntegerXBox)
                    integerBoxList.append(IntegerYBox)
                    integerBoxList.append(IntegerZBox)
                    self.intDict[bone] = integerBoxList
                    AddXBox = lConstraintRelation.CreateFunctionBox('Number', 'Add (a + b)')
                    AddYBox = lConstraintRelation.CreateFunctionBox('Number', 'Add (a + b)')
                    AddZBox = lConstraintRelation.CreateFunctionBox('Number', 'Add (a + b)')
                    numberToVectorBox = lConstraintRelation.CreateFunctionBox('Converters', 'Number to Vector')
                    receiverBox = lConstraintRelation.ConstrainObject(bone)
                    lConstraintRelation.SetBoxPosition(senderBox, 0, 0)
                    lConstraintRelation.SetBoxPosition(vectorToNumberBox, 250, 200)
                    lConstraintRelation.SetBoxPosition(IntegerXBox, 250, -300)
                    lConstraintRelation.SetBoxPosition(IntegerYBox, 250, -200)
                    lConstraintRelation.SetBoxPosition(IntegerZBox, 250, -100)
                    lConstraintRelation.SetBoxPosition(AddXBox, 550, 0)
                    lConstraintRelation.SetBoxPosition(AddYBox, 550, 100)
                    lConstraintRelation.SetBoxPosition(AddZBox, 550, 200)
                    lConstraintRelation.SetBoxPosition(numberToVectorBox, 850, 0)
                    lConstraintRelation.SetBoxPosition(receiverBox, 1150, 0)
                    senderRotationNode = find_animation_node(senderBox.AnimationNodeOutGet(), 'Rotation')
                    vectorToNumberInNode = find_animation_node(vectorToNumberBox.AnimationNodeInGet(), 'V')
                    vectorToNumberXOutNode = find_animation_node(vectorToNumberBox.AnimationNodeOutGet(), 'X')
                    vectorToNumberYOutNode = find_animation_node(vectorToNumberBox.AnimationNodeOutGet(), 'Y')
                    vectorToNumberZOutNode = find_animation_node(vectorToNumberBox.AnimationNodeOutGet(), 'Z')
                    IntegerXNode = find_animation_node(IntegerXBox.AnimationNodeOutGet(), 'Result')
                    IntegerYNode = find_animation_node(IntegerYBox.AnimationNodeOutGet(), 'Result')
                    IntegerZNode = find_animation_node(IntegerZBox.AnimationNodeOutGet(), 'Result')
                    AddAXInNode = find_animation_node(AddXBox.AnimationNodeInGet(), 'a')
                    AddAYInNode = find_animation_node(AddYBox.AnimationNodeInGet(), 'a')
                    AddAZInNode = find_animation_node(AddZBox.AnimationNodeInGet(), 'a')
                    AddBXInNode = find_animation_node(AddXBox.AnimationNodeInGet(), 'b')
                    AddBYInNode = find_animation_node(AddYBox.AnimationNodeInGet(), 'b')
                    AddBZInNode = find_animation_node(AddZBox.AnimationNodeInGet(), 'b')
                    AddXOutNode = find_animation_node(AddXBox.AnimationNodeOutGet(), 'Result')
                    AddYOutNode = find_animation_node(AddYBox.AnimationNodeOutGet(), 'Result')
                    AddZOutNode = find_animation_node(AddZBox.AnimationNodeOutGet(), 'Result')
                    numberToVectorXInNode = find_animation_node(numberToVectorBox.AnimationNodeInGet(), 'X')
                    numberToVectorYInNode = find_animation_node(numberToVectorBox.AnimationNodeInGet(), 'Y')
                    numberToVectorZInNode = find_animation_node(numberToVectorBox.AnimationNodeInGet(), 'Z')
                    numberToVectorOutNode = find_animation_node(numberToVectorBox.AnimationNodeOutGet(), 'Result')
                    receiverRotationNode = find_animation_node(receiverBox.AnimationNodeInGet(), 'Rotation')
                    FBConnect(senderRotationNode, vectorToNumberInNode)
                    FBConnect(IntegerXNode, AddAXInNode)
                    FBConnect(IntegerYNode, AddAYInNode)
                    FBConnect(IntegerZNode, AddAZInNode)
                    FBConnect(vectorToNumberXOutNode, AddBXInNode)
                    FBConnect(vectorToNumberYOutNode, AddBYInNode)
                    FBConnect(vectorToNumberZOutNode, AddBZInNode)
                    FBConnect(AddXOutNode, numberToVectorXInNode)
                    FBConnect(AddYOutNode, numberToVectorYInNode)
                    FBConnect(AddZOutNode, numberToVectorZInNode)
                    FBConnect(numberToVectorOutNode, receiverRotationNode)
                    if folderSwitch == False:
                        fingerToolFolder = FBFolder("FingerToolFolder", lConstraintRelation)
                        folderSwitch = True
                    else:
                        fingerToolFolder.ConnectSrc(lConstraintRelation)
                else:
                    print ("Constraints already exist")
                    break
        except:
            print ("no bones found")
            pass
        
        
#FB TOOL       
class NativeQtWidgetTool(FBTool):
    """
    An FBTool instance that wraps our FBWidgetHolder
    """
    def __init__(self, name):
        FBTool.__init__(self, name)
        self.mNativeWidgetHolder = NativeWidgetHolder();
        self.build_layout()
        
        self.StartSizeX = 750
        self.StartSizeY = 825
        self.MinSizeX = 200
        self.MinSizeY = 200

    def build_layout(self):
        x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
        self.AddRegion("main","main", x, y, w, h)
        self.SetControl("main", self.mNativeWidgetHolder)      


#GENERAL FUNCTIONS

#Find all input or output nodes in a constraint box
def find_animation_node(pParent, pName):
    l_result = None
    for lNode in pParent.Nodes:
        if lNode.Name == pName:
            l_result = lNode
            break
    return l_result

#Iterate through hand bone hierarchy
def store_children(hand, handBoneList):
    try:
        for bone in hand.Children:
            handBoneList.append(bone)
            store_children(bone, handBoneList)
    except:
        print("hand bones not found")

#Create FBTool 
def run_fbtool():
    if DEVELOPMENT:
        #FBDestroyToolByName(NAME)
        #FBSystem().Scene.Evaluate()
        pass
    
    if NAME in FBToolList:
        tool = FBToolList[NAME]
        ShowTool(tool)

    else:
        tool=NativeQtWidgetTool(NAME)
        FBAddTool(tool)
        ShowTool(tool)
        
if __name__ == '__builtin__':
    run_fbtool()
    
    
    

#TO DO:
# rightHand = FBFindModelByLabelName('_1:Solving:RightHand') needs to search via talent ID not _1
# Finger Solver constraint needs to be turned off to work properly
# Only left hand joints move. All other joints need to be connected
# Checkboxes need to move both right and left joints
# remove_window_clicked does not destroy the tool properly. The cleanup process needs to be fixed
# If there is no skeleton in the scene when the code is run, you will need to load a new scene to get the script to work

#List of Integer function box numbers for all constraints
#xList = ["Integer",3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78,81,84,87,90,93,96,99,102,105,108,111,114,117,120,123,126,129,132,135,138,141,144,147]
#yList = [1,4,7,10,13,16,19,22,25,28,31,34,37,40,43,46,49,52,55,58,61,64,67,70,73,76,79,82,85,88,91,94,97,100,103,106,109,112,115,118,121,124,127,130,133,136,139,142,145,148]
#zList = [2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59,62,65,68,71,74,77,80,83,86,89,92,95,98,101,104,107,110,113,116,119,122,125,128,131,134,137,140,143,146,149]

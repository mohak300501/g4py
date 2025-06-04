"""
g4py/g4params.py
- QDialog to set parameters for a Geant4 detector/particle simulation
"""

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QDialogButtonBox, QComboBox, QMessageBox, QScrollArea, QHeaderView,
                             QTableWidget, QTableWidgetItem, QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton)
from PyQt5 import QtCore
import sys, os, shutil, csv, subprocess
from pathlib import Path
import tempvars

absPath  = Path().absolute()

class Node:
    def __init__(self, name, density, ratio, parent=None):
        self.name = name
        self.density = density
        self.ratio = ratio
        self.parent = parent
        self.children = []

class DAG:
    """ Directed Acyclic Graph """

    def __init__(self):
        self.nodes = {}
        self.temps = {}

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_edge(self, parent_name, node_name):
        if parent_name in self.nodes:
            parent = self.nodes[parent_name]
            child = self.nodes[node_name]
            parent.children.append(child)
            child.parent = parent

        elif len(parent_name):
            if parent_name in self.temps:
                self.temps[parent_name].append(self.nodes[node_name])
            else:
                self.temps[parent_name] = [self.nodes[node_name]]

        if node_name in self.temps:
            parent = self.nodes[node_name]
            for child in self.temps[node_name]:
                parent.children.append(child)
                child.parent = parent

    def traverse(self):
        traversal_order = []

        def dfs(node):
            for child in node.children:
                dfs(child)
            traversal_order.append(node)

        n = 0
        for node in self.nodes:
            if not self.nodes[node].parent:
                self.start_node = self.nodes[node]
                n += 1

        if n != 1:
            return None

        dfs(self.start_node)
        return traversal_order[::-1]



class G4PY(QMainWindow):
    def __init__(self):
        super(G4PY, self).__init__(parent=None)
        self.setWindowTitle("Geant4 Params")

        self.centralWidget = QScrollArea(self)
        self.centralWidget.setVerticalScrollBarPolicy  (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.centralWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.centralWidget.setWidgetResizable(True)
        self.setCentralWidget(self.centralWidget)

        self.paramsWidget = QWidget(self.centralWidget)
        self.paramsLayout = QVBoxLayout(self.paramsWidget)
        self.centralWidget.setWidget(self.paramsWidget)

        self.values = []
        try:
            with open(f"{absPath}/{absPath.name}.txt", "r") as f:
                for line in f:
                    self.values.append(line.strip())
        except:
            QMessageBox.critical(self, "Error", f"`{absPath.name}.txt` not found")
            sys.exit(self.close())

        if not len(self.values):
            QMessageBox.critical(self, "Error", "Template data not available.")
            sys.exit(self.close())

        #------------------------------------------------------------------

        self.widget0 = QWidget(self)
        self.widget0Layout = QHBoxLayout(self.widget0)
        self.paramsLayout.addWidget(self.widget0)

        self.groupbox0 = QGroupBox("Preliminaries", self.widget0)
        self.groupbox0Layout = QFormLayout(self.groupbox0)
        self.groupbox0Layout.setVerticalSpacing(  int(width * 0.02))
        self.groupbox0Layout.setHorizontalSpacing(int(width * 0.04))
        self.widget0Layout.addWidget(self.groupbox0)

        self.dir = QLineEdit(self.groupbox0)
        self.pmt = QComboBox(self.groupbox0)
        self.pmt  .addItems(["No", "Yes"])
        self.dir  .setText       (self.values[0])
        self.pmt  .setCurrentText(self.values[1])

        labels0 = ["Directory name", "Do you need PMTs?"]
        fields0 = [self.dir, self.pmt]

        for i in range(len(fields0)):
            self.groupbox0Layout.addRow(labels0[i], fields0[i])

        self.widget0Layout.addSpacing(int(width * 0.02))

        #------------------------------------------------------------------

        self.groupbox1 = QGroupBox("Particle Params", self.widget0)
        self.groupbox1Layout = QFormLayout(self.groupbox1)
        self.groupbox1Layout.setVerticalSpacing(  int(width * 0.02))
        self.groupbox1Layout.setHorizontalSpacing(int(width * 0.04))

        self.particle = QLineEdit(self.groupbox1)
        self.partProp = QComboBox(self.groupbox1)
        self.partVal  = QLineEdit(self.groupbox1)
        self.partProp  .addItems(["Energy", "Momentum"])
        self.particle  .setText       (self.values[2])
        self.partProp  .setCurrentText(self.values[3])
        self.partVal   .setText       (self.values[4])

        labels1 = ["Particle", "Property", "Value"]
        fields1 = [self.particle, self.partProp, self.partVal]

        for i in range(len(fields1)):
            self.groupbox1Layout.addRow(labels1[i], fields1[i])

        self.widget0Layout.addWidget(self.groupbox1)

        #------------------------------------------------------------------

        self.widget1 = QWidget(self)
        self.widget1Layout = QHBoxLayout(self.widget1)
        self.paramsLayout.addWidget(self.widget1)

        self.groupbox2 = QGroupBox("World", self.widget1)
        self.groupbox2Layout = QFormLayout(self.groupbox2)
        self.groupbox2Layout.setVerticalSpacing(  int(width * 0.02))
        self.groupbox2Layout.setHorizontalSpacing(int(width * 0.04))
        self.widget1Layout.addWidget(self.groupbox2)

        self.worldDims = QLineEdit(self.values[5], self.groupbox2)
        self.worldMat  = QLineEdit(self.values[6], self.groupbox2)

        labels2 = ["Dimensions", "Material"]
        fields2 = [self.worldDims, self.worldMat]

        for i in range(len(fields2)):
            self.groupbox2Layout.addRow(labels2[i], fields2[i])

        self.widget1Layout.addSpacing(int(width * 0.02))

        #------------------------------------------------------------------

        self.groupbox3 = QGroupBox("Detector Box", self.widget1)
        self.groupbox3Layout = QFormLayout(self.groupbox3)
        self.groupbox3Layout.setVerticalSpacing(  int(width * 0.02))
        self.groupbox3Layout.setHorizontalSpacing(int(width * 0.04))
        self.widget1Layout.addWidget(self.groupbox3)

        self.detDims = QLineEdit(self.values[7] , self.groupbox3)
        self.detPVPz = QLineEdit(self.values[8] , self.groupbox3)

        labels3 = ["Dimensions", "Placement (z)"]
        fields3 = [self.detDims, self.detPVPz]

        for i in range(len(fields3)):
            self.groupbox3Layout.addRow(labels3[i], fields3[i])

        #------------------------------------------------------------------

        self.widget2 = QWidget(self)
        self.widget2Layout = QHBoxLayout(self.widget2)
        self.paramsLayout.addWidget(self.widget2)

        self.groupbox4 = QGroupBox("Detector Materials", self)
        self.groupbox4Layout = QFormLayout(self.groupbox4)
        self.groupbox4Layout.setVerticalSpacing(  int(width * 0.005))
        self.groupbox4Layout.setHorizontalSpacing(int(width * 0.04))
        self.widget2Layout.addWidget(self.groupbox4)

        self.parents = set()

        self.em        = QComboBox(self.groupbox4)
        self.emname    = QLineEdit(self.groupbox4)
        self.emratio   = QLineEdit(self.groupbox4)
        self.emparent  = QComboBox(self.groupbox4)
        self.em         .addItems(["element", "material"])
        self.emname     .setText("H")
        self.emratio    .setText("2")
        self.em.currentIndexChanged.connect(self.emset)
        
        self.emdensity = QLineEdit("", None)

        fields4 = [self.em, self.emname, self.emratio, self.emparent]
        labels4 = ["Element/material", "Name", "Ratio", "Parent"]

        for i in range(len(fields4)):
            self.groupbox4Layout.addRow(labels4[i], fields4[i])

        self.addBtn = QPushButton("Add", self.groupbox4)
        self.addBtn.clicked.connect(self.addToTable)
        self.groupbox4Layout.addWidget(self.addBtn)

        self.widget2Layout.addSpacing(int(width * 0.02))

        #------------------------------------------------------------------

        self.groupbox5 = QGroupBox("Materials Table", self)
        self.groupbox5Layout = QFormLayout(self.groupbox5)
        self.widget2Layout.addWidget(self.groupbox5)

        labels5 = ["Name", "\u03C1", "Ratio", "Parent", ""]

        self.emtable = QTableWidget(0, len(labels5), self.groupbox4)
        self.emtable.setHorizontalHeaderLabels(labels5)
        self.emtable.horizontalHeader().setStretchLastSection(True)
        self.emtable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.groupbox5Layout.addWidget(self.emtable)

        with open(f"{absPath}/mat.csv", "r") as f:
            readCSV = list(csv.reader(f))
        self.makeTable(readCSV)

        self.emparent.addItems(self.parents)

        #------------------------------------------------------------------

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok |
                                          QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)
        self.paramsLayout.addWidget(self.buttonBox)

    #----------------------------------------------------------------------

    def emset(self):
        if self.em.currentIndex():
            self.emdensity = QLineEdit("1.000", self.groupbox4)
            self.groupbox4Layout.insertRow(3, "Density (g/cm3)", self.emdensity)
        else:
            self.emdensity = QLineEdit(""     , self.groupbox4)
            self.groupbox4Layout.removeRow(3)

    #----------------------------------------------------------------------

    def makeTable(self, readCSV):
        self.emtable.setRowCount(len(readCSV))

        for i in range(len(readCSV)):
            for j in range(4):
                self.emtable.setItem(i, j, QTableWidgetItem(readCSV[i][j]))
            self.parents.add(readCSV[i][3])

            removeBtn = QPushButton("Remove", self.emtable)
            removeBtn.clicked.connect(lambda _, row=i: self.removeFromTable(row))
            self.emtable.setCellWidget(i, 4, removeBtn)

    #----------------------------------------------------------------------

    def addToTable(self):
        with open(f"{absPath}/mat.csv", "r") as f:
            readCSV = list(csv.reader(f))

        data =  [self.emname   .       text(),
                 self.emdensity.       text(),
                 self.emratio  .       text(),
                 self.emparent .currentText()]

        if data in readCSV:
            QMessageBox.critical(self, "Error", "Material already exists.")
            return

        readCSV.append(data)
        readCSV = sorted(readCSV, key=lambda x: [x[-1], x[0]])

        self.makeTable(readCSV)

        writeCSV = csv.writer(open(f"{absPath}/mat.csv", "w"))
        writeCSV.writerows(readCSV)

        if self.em.currentIndex(): self.emparent.addItem(self.emname.text())

    #----------------------------------------------------------------------

    def removeFromTable(self, row):
        with open(f"{absPath}/mat.csv", "r") as f:
            readCSV = list(csv.reader(f))

        readCSV.pop(row)
        readCSV = sorted(readCSV, key=lambda x: (x[-1], x[0]))

        self.makeTable(readCSV)

        writeCSV = csv.writer(open(f"{absPath}/mat.csv", "w"))
        writeCSV.writerows(readCSV)

    #----------------------------------------------------------------------

    def accept(self):
        fields = [self.dir      .text(), self.pmt     .currentText(),
                  self.particle .text(), self.partProp.currentText(), self.partVal.text(),
                  self.worldDims.text(), self.worldMat.text(),
                  self.detDims  .text(), self.detPVPz .text()]

        try:
            if absPath.name != fields[0]:
                dirPath = f"{os.path.dirname(absPath)}/{fields[0]}"
                os.makedirs(dirPath)

                for file in os.listdir(f"{absPath}"):
                    if os.path.isfile(f"{absPath}/{file}"):
                        shutil.copyfile(f"{absPath}/{file}", f"{dirPath}/{file}")

                if os.path.isfile(f"{dirPath}/{absPath.name}.txt"):
                    os.remove(f"{dirPath}/{absPath.name}.txt")

            else:
                dirPath = absPath

            with open(f"{dirPath}/{fields[0]}.txt", 'w') as file:
                for field in fields:
                    file.write(f"{field}\n")

            #**************************************** CREATE FILE generator.cc ****************************************

            with open(f"{dirPath}/generator.cc", "w") as genccfile:
                genccfile.write(tempvars.gencc % (fields[2],
                                                    f"{fields[3]}({fields[4]})"))

            #************************************** CREATE FILE construction.cc ***************************************

            with open(f"{dirPath}/construction.cc", "w") as conccfile:

                with open(f"{dirPath}/mat.csv", "r") as matfile:
                    readCSV = list(csv.reader(matfile))

                # Create the DAG and populate it with nodes and edges
                dag = DAG()
                for row in readCSV:
                    name, density, ratio, parent = row
                    node = Node(name, density, ratio)
                    dag.add_node(node)
                    dag.add_edge(parent, name)

                # Use the DAG to generate the output code
                traversal_order = dag.traverse()
                if not traversal_order:
                    QMessageBox.critical(self, "Error", "Please configure only 1 material with parent field left blank.")
                    return

                matList = set()
                ccstr   = ""

                for node in traversal_order:
                    if len(node.density):
                        matList.add(f"*{node.name}")

                        ccstr     += f"    {node.name} = new G4Material(\"{node.name}\", {node.density}*g/cm3, {len(node.children)});\n"

                        if node.parent:
                            ccstr += f"    {node.parent.name} -> AddMaterial({node.name}, {node.ratio});\n"

                    else:
                        ccstr     += f"    {node.parent.name} -> AddElement(nist -> FindOrBuildElement(\"{node.name}\"), {node.ratio});\n"

                conccfile.write(tempvars.concc % (self.worldMat.text(),
                                                    ccstr,
                                                    *fields[5].split(","),
                                                    *fields[7].split(","), fields[8],
                                                    dag.start_node.name,
                                                    tempvars.pmt if fields[1] else "",
                                                    "logicPMT" if fields[1] else "logicDetector"))

            #************************************** CREATE FILE construction.hh ***************************************

            with open(f"{dirPath}/construction.hh", "w") as conhhfile:
                conhhfile.write(tempvars.conhh % (', ').join(matList))

            #**********************************************************************************************************

            self.close()

            buildPath = f"{dirPath}/build"
            if not os.path.exists(buildPath):
                os.makedirs(buildPath)
            os.chdir(buildPath)

            subprocess.run(["cmake", dirPath])
            subprocess.run(["make"])

        except OSError as e:
            QMessageBox.critical(self, "Error", f"{e}")
            return



app = QApplication(sys.argv)

screenSize = app.primaryScreen().size()
width, height = screenSize.width(), screenSize.height()

window = G4PY()

styleSheet = Path(f"{absPath}/style.qss").read_text()
fontSizes = (int(width * 0.016), int(width * 0.06), int(width * 0.06))
app.setStyleSheet(styleSheet % fontSizes)

window.showMaximized()
app.exec()

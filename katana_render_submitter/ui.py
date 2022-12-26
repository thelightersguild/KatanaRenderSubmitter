from PyQt5 import QtWidgets, QtCore
import sys

from katana_render_submitter import core

#TODO rename widget
class RenderPassTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(RenderPassTree, self).__init__(parent)
        self.arrange_layout()
        #self.set_data()
        self.connect_signals()
        #self.resizeColumnsToContents()
        #self.resizeColumnsToContents()
        #self.resizeRowsToContents()

    def arrange_layout(self):
        self.setColumnCount(4)
        self.setHeaderLabels(['category', 'RenderPass', 'FrameRange', 'Version'])

    #TODO should be called populate tree or something
    def set_data(self):
        data = core.get_renderpass_data()
        render_categories = list()
        for key, values in data.items():
            item = QtWidgets.QTreeWidgetItem([key])
            for value in values:
                child = QtWidgets.QTreeWidgetItem(['', value, '1121-1266', 'V+'])
                item.addChild(child)
                child.setCheckState(0, QtCore.Qt.Checked)
            render_categories.append(item)
        self.insertTopLevelItems(0, render_categories)

    def connect_signals(self):
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self:
            self.selected_items = self.selectedItems()
            if len(self.selected_items) > 0:
                menu = QtWidgets.QMenu()
                custom_action = QtWidgets.QAction('Custom')
                menu.addAction(custom_action)
                menu.addAction('FML')
                menu.addAction('x10')
                custom_action.triggered.connect(self.set_custom_framerange_dialog)
                if menu.exec_(event.globalPos()):
                    item = source.itemAt(event.pos())
                return True
        return super().eventFilter(source, event)

    def set_custom_framerange_dialog(self):
        text, ok = QtWidgets.QInputDialog().getText(
            self, "QInputDialog().getText()",
            "User name:",
            QtWidgets.QLineEdit.Normal
        )
        if ok and text:
            #TODO add check for formatting of range
            frame_range = text
            self.update_item_columns(self.selected_items, 2, frame_range)

    def update_item_columns(self, widget_items, column, value):
        for widget_item in widget_items:
            widget_item.setText(column, value)


class KatanaRenderSubmitterWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(layout_main)
        self.render_pass_tree = RenderPassTree()
        layout_main.addWidget(self.render_pass_tree)
        render_widget_layout = QtWidgets.QHBoxLayout()
        layout_main.addLayout(render_widget_layout)
        self.render_button = QtWidgets.QPushButton('Launch Render')
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        render_widget_layout.addWidget(self.render_button)
        render_widget_layout.addWidget(self.refresh_button)
        self.connect_signals()

    def update_data(self):
        data = core.get_renderpass_data()
        self.render_pass_tree.set_data()


    def connect_signals(self):
        self.render_button.clicked.connect(self.launch_render_btn_clicked)
        self.refresh_button.clicked.connect(self.refresh_btn_clicked)

    def launch_render_btn_clicked(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.render_pass_tree,
            flags=QtWidgets.QTreeWidgetItemIterator.Checked
         )
        jobs = list()
        while iterator.value():
            item = iterator.value()
            pass_name = item.text(1)
            frame_range = item.text(2)
            render_job = core.Job(pass_name, frame_range, 'V+')
            #TODO put a is_valid attribute in Job as a preflight check
            jobs.append(render_job)
            iterator += 1
        #submit jobs
        core.package_job(jobs)

    def refresh_btn_clicked(self):
        self.render_pass_tree.clear()
        self.update_data()


def launch_ui(*args):
    # running from terminal
    if args:
        app = QtWidgets.QApplication(args)
    print ('this is runnning')
    x = Window()
    x.show()
    if args:
        sys.exit(app.exec_())

'''    
import importlib
from katana_render_submitter import core, ui

importlib.reload(core)
importlib.reload(ui)


x = ui.Window()
x.show()
'''
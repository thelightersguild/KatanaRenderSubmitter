from PyQt5 import QtWidgets, QtCore
import sys
from functools import partial

from katana_render_submitter import core

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
                # frame range actions
                frame_range_title_action = menu.addAction("Set Frame Range")
                frame_range_title_action.setEnabled(False)
                custom_frame_action = menu.addAction(' Custom')
                x10_action = menu.addAction(' 10s')
                fml_action =  menu.addAction(' FML')
                x1_action = menu.addAction(' 1s')
                # versioning actions
                version_title_action = menu.addAction("Set Version")
                version_title_action.setEnabled(False)
                version_up_action = menu.addAction(' Version Up')
                custom_version_action = menu.addAction(' Custom Version')
                #signals
                #framerange
                custom_frame_action.triggered.connect(partial(self.set_frame_range_action, 'custom'))
                x10_action.triggered.connect(partial(self.set_frame_range_action, 'x10'))
                fml_action.triggered.connect(partial(self.set_frame_range_action, 'FML'))
                x1_action.triggered.connect(partial(self.set_frame_range_action, 'x1'))
                # versioning
                version_up_action.triggered.connect(partial(self.set_version_action, 'V+'))
                custom_version_action.triggered.connect(partial(self.set_version_action, 'custom'))
                #draw menu
                if menu.exec_(event.globalPos()):
                    item = source.itemAt(event.pos())
                return True
        return super().eventFilter(source, event)

    def set_frame_range_action(self, type):
        frame_range = None
        if type == 'x10':
            frame_range = 'x10'
        if type == 'x1':
            frame_range = '1121-1266'
        if type == 'FML':
            frame_range = 'FML'
        if type == 'custom':
            frame_range = self.user_input_dialog(
                'Set Custom Frame Range',
                'Specify frame range (e.g 1001-1030)'
            )
            if frame_range is None:
                return
        self.update_item_columns(self.selected_items, 2, frame_range)

    def user_input_dialog(self, title, description):
        dialog = QtWidgets.QInputDialog()
        text, ok = dialog.getText(
            self,
            title,
            description,
            QtWidgets.QLineEdit.Normal
        )
        if ok and text:
            #TODO add check for formatting of range
            value = text
            return value
        else:
            return None


    def set_version_action(self, type):
        version = None
        if type == 'V+':
            version = 'V+'
        if type == 'custom':
            version = self.user_input_dialog(
                'Set Custom Version',
                'Specify version number'
            )
            if version:
                version = f'{int(version):02d}'
        if version:
            self.update_item_columns(self.selected_items, 3, version)


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
        self.render_local_cbox = QtWidgets.QCheckBox("Render Local")
        render_widget_layout.addWidget(self.render_local_cbox)
        render_widget_layout.addWidget(self.render_button)
        render_widget_layout.addWidget(self.refresh_button)
        self.connect_signals()

    def update_data(self):
        #data = core.get_renderpass_data()
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
            version = item.text(3)
            render_job = core.Job(pass_name, frame_range, version)
            #TODO put a is_valid attribute in Job as a preflight check
            jobs.append(render_job)
            iterator += 1
        #submit jobs
        state = self.render_local_cbox.checkState()
        if state == 2:
            force_cloud = "0"
        elif state == 0:
            force_cloud = "1"
        core.package_job(jobs, force_cloud)

    def refresh_btn_clicked(self):
        self.render_pass_tree.clear()
        self.update_data()


def launch_ui(*args):
    # running from terminal
    if args:
        app = QtWidgets.QApplication(args)

    x = Window()
    x.show()
    if args:
        sys.exit(app.exec_())

'''    
import importlib
from katana_render_submitter import core, ui

importlib.reload(core)
importlib.reload(ui)


x = ui.KatanaRenderSubmitterWidget()
x.show()
'''
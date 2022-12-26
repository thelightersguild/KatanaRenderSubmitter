from Katana import UI4
from PyQt5 import QtWidgets

from katana_render_submitter import ui

class KatanaRenderSubmitterTab(UI4.Tabs.BaseTab):
    def __init__(self, parent):
        UI4.Tabs.BaseTab.__init__(self, parent)
        central_widget = ui.KatanaRenderSubmitterWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(central_widget)
        self.setLayout(main_layout)

PluginRegistry = [
    ('KatanaPanel', 2.0, 'KatanaRenderSubmitter', KatanaRenderSubmitterTab),
]
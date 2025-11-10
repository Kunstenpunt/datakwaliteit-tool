import sys, textwrap

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from __feature__ import snake_case, true_property

from backend.wikibasehelper import BASE_URL, WikibaseHelper
from backend.constraints import ConstraintAnalyzer
from backend.utils import url_from_id

from ui.constrainttab import Ui_ConstraintTab
from ui.mainwindow import Ui_MainWindow
from ui.querytab import Ui_QueryTab


def on_table_double_clicked(index):
    possible_id = index.data()
    url = url_from_id(possible_id, BASE_URL)
    if url:
        QDesktopServices.open_url(QUrl(url))


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row() + 1][index.column()]

    def row_count(self, index):
        return len(self._data) - 1

    def column_count(self, index):
        return len(self._data[0])

    def header_data(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data[0][section]


class Model:
    def __init__(self):
        self.wikibase_helper = WikibaseHelper()
        self.wikibase_helper.login()
        self.constraint_analyzer = ConstraintAnalyzer(self.wikibase_helper)


class QueryTab(QWidget, Ui_QueryTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.execute_button.clicked.connect(self.on_execute_button_clicked)
        self.table_view.doubleClicked.connect(on_table_double_clicked)

    def on_execute_button_clicked(self):
        query = self.plain_text_edit.plain_text
        result = self.model.wikibase_helper.execute_query(query, self.on_query_result)

    def on_query_result(self):
        result = self.model.wikibase_helper.query_result
        if not result:
            return
        result_model = QSortFilterProxyModel()
        result_model.set_source_model(SimpleTableModel(result))
        self.table_view.set_model(result_model)
        self.table_view.horizontal_header().resize_sections(
            QHeaderView.ResizeMode.ResizeToContents
        )


class ConstraintsTab(QWidget, Ui_ConstraintTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model
        self.splitter.set_stretch_factor(0, 2)
        self.splitter.set_stretch_factor(1, 1)
        self.validate_button.enabled = False

        self.reload_button.clicked.connect(self.on_reload_button_clicked)
        self.validate_button.clicked.connect(self.on_validate_button_clicked)
        self.properties_table_view.clicked.connect(self.on_property_clicked)
        self.properties_table_view.doubleClicked.connect(on_table_double_clicked)
        self.violations_table_view.doubleClicked.connect(on_table_double_clicked)
        self.model.constraint_analyzer.constrainedPropertiesUpdated.connect(
            self.on_constrained_properties_updated
        )
        self.model.constraint_analyzer.focusedPropertyConstraintUpdated.connect(
            self.on_focused_property_constraint_updated
        )

    def on_reload_button_clicked(self):
        self.model.constraint_analyzer.update_constraints()

    def on_constrained_properties_updated(self):
        header = ["Prop ID", "Prop label", "Constraint ID", "Constraint Label", "Implemented"]
        data = [
            header
        ] + self.model.constraint_analyzer.get_constraints_list_full()
        sortable_data_model = QSortFilterProxyModel()
        sortable_data_model.set_source_model(SimpleTableModel(data))
        self.properties_table_view.set_model(sortable_data_model)
        self.properties_table_view.horizontal_header().resize_sections(
            QHeaderView.ResizeMode.ResizeToContents
        )

    def on_property_clicked(self, index):
        table_model = index.model()
        prop_id = table_model.data(table_model.index(index.row(), 0))
        constraint_id = table_model.data(table_model.index(index.row(), 2))
        self.model.constraint_analyzer.set_focused_constraint(
            prop_id, constraint_id
        )

    def on_focused_property_constraint_updated(self):
        focused_property_constraint = (
            self.model.constraint_analyzer.focused_constraint
        )
        focused_property_constraint.violationsUpdated.connect(
            self.update_violations_table_view
        )
        self.label_right.text = focused_property_constraint.pretty()
        self.validate_button.enabled = focused_property_constraint.implemented
        self.update_violations_table_view()

    def on_validate_button_clicked(self):
        focused_property_constraint = (
            self.model.constraint_analyzer.focused_constraint
        )
        focused_property_constraint.query_violations()

    def update_violations_table_view(self):
        data = self.model.constraint_analyzer.focused_constraint.violations
        if data == None:
            self.violations_table_view.set_model(None)
            return
        sortable_data_model = QSortFilterProxyModel()
        sortable_data_model.set_source_model(SimpleTableModel(data))
        self.violations_table_view.set_model(sortable_data_model)
        self.violations_table_view.horizontal_header().resize_sections(
            QHeaderView.ResizeMode.ResizeToContents
        )


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = Model()

        self.tab_widget.add_tab(ConstraintsTab(self.model), "Constraints")
        self.tab_widget.add_tab(QueryTab(self.model), "Query")
        self.query_indicator = QProgressBar()
        self.query_indicator.set_range(0, 0)
        self.query_indicator.maximum_width = 128
        self.statusbar.add_widget(self.query_indicator)
        self.query_indicator.hide()

        self.copy_query_button = QPushButton()
        self.copy_query_button.text = "Copy Last Query to Clipboard"
        self.copy_query_button.clicked.connect(self.copy_query_to_clipboard)
        self.statusbar.add_permanent_widget(self.copy_query_button)

        self.model.wikibase_helper.query_started.connect(self.query_indicator.show)
        self.model.wikibase_helper.query_done.connect(self.query_indicator.hide)

    def copy_query_to_clipboard(self):
        prefixes = textwrap.dedent(self.model.wikibase_helper.query_prefixes).lstrip()
        query = textwrap.dedent(self.model.wikibase_helper.most_recent_query).lstrip()
        clipboard = QGuiApplication.clipboard()
        clipboard.set_text(f"{prefixes}\n{query}")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()

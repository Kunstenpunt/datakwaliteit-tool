from PySide6.QtCore import (
    QFileInfo,
    QModelIndex,
    QSortFilterProxyModel,
    QStandardPaths,
    Qt,
)
from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtSql import QSqlTableModel

from ..backend.constraint.base import Constraint, ValidationMode, ValidationState
from ..backend.export import Exporter
from ..backend.model import Model
from ..backend.sql import SqlDatabase

from .designer.constrainttab import Ui_ConstraintTab
from .simpletablemodel import (
    headerResizeNeatly,
    SqlTableModel,
    TableClickHandler,
)


class ConstraintsTab(QWidget, Ui_ConstraintTab):
    def __init__(self, model: Model) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self._model = model
        self._exporter = Exporter(self._model.wikibaseConfig)
        self._exportDir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation,
        )
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.validateButton.setEnabled(False)
        self.exportButton.setEnabled(False)

        self.reloadButton.clicked.connect(self._updateConstraints)
        self.validateAllButton.clicked.connect(self._validateAll)
        self.validateButton.clicked.connect(self._startValidation)
        self.exportAllButton.clicked.connect(self._exportAll)
        self.exportButton.clicked.connect(self._exportSingleConstraint)
        self.limitComboBox.currentIndexChanged.connect(self._changeLimitMode)
        self._changeLimitMode()
        self.sortedCheckBox.checkStateChanged.connect(self._changeLimitSorted)
        self._changeLimitSorted()
        self._tableClickHandler = TableClickHandler(self._model.wikibaseConfig)
        self.constraintsTableView.doubleClicked.connect(
            self._tableClickHandler.onTableDoubleClicked
        )
        self.violationsTableView.doubleClicked.connect(
            self._tableClickHandler.onTableDoubleClicked
        )
        self._model.constraintCheckModel.focusedConstraintUpdated.connect(
            self._onFocusedConstraintUpdated
        )
        self._model.constraintCheckModel.focusedConstraintInputCountUpdated.connect(
            self._updateFocusedConstraintInputCount
        )
        self._model.constraintCheckModel.focusedConstraintQualifiersUpdated.connect(
            self._updateFocusedConstraintLabel
        )
        self._model.constraintCheckModel.validateAllDone.connect(
            self._updateValidateAllLabel
        )

        self._model.sqlDatabase.tableAdded.connect(self._reloadConstraintsTable)
        self._model.sqlDatabase.tableAdded.connect(self._loadViolations)
        self._model.sqlDatabase.tableUpdated.connect(self._updateConstraintsTable)

        self.constraintsTableModel = SqlTableModel()
        self.constraintsTableView.setModel(self.constraintsTableModel)
        self.constraintsTableModel.selectionModel = (
            self.constraintsTableView.selectionModel()
        )
        self.constraintsTableView.selectionModel().currentChanged.connect(
            self._onConstraintSelectionChanged
        )

        self.violationsTableModel = SqlTableModel()
        self.violationsTableView.setModel(self.violationsTableModel)
        self.violationsTableModel.selectionModel = (
            self.violationsTableView.selectionModel()
        )

    def _updateConstraints(self) -> None:
        self._model.constraintCheckModel.queryConstraints()

    def _reloadConstraintsTable(self, table: str) -> None:
        if table != "constraints":
            return

        self.constraintsTableModel.setTable(table)
        headerLabels = [
            "Row ID",
            "Prop ID",
            "Prop label",
            "Constraint ID",
            "Constraint Label",
            "Implemented",
            "Validated",
        ]
        for i, headerLabel in enumerate(headerLabels):
            self.constraintsTableModel.setHeaderData(
                i, Qt.Orientation.Horizontal, headerLabel
            )
        self.constraintsTableModel.select()
        self.constraintsTableView.hideColumn(0)
        headerResizeNeatly(self.constraintsTableView.horizontalHeader())

        try:
            self.constraintsTableView.selectRow(0)
        except:
            pass

    def _updateConstraintsTable(self, table: str, rowId: int) -> None:
        if table != "constraints":
            return

        self.constraintsTableModel.select()

    def _onConstraintSelectionChanged(
        self, current: QModelIndex, _: QModelIndex
    ) -> None:
        if current == None:
            return
        tableModel = current.model()
        rowId = tableModel.data(tableModel.index(current.row(), 0))
        self._model.constraintCheckModel.setFocusedConstraint(rowId)

    def _onFocusedConstraintUpdated(self) -> None:
        focusedConstraint = self._model.constraintCheckModel.focusedConstraint
        if not focusedConstraint:
            return
        self._updateFocusedConstraintLabel()
        self._updateFocusedConstraintInputCount()
        self.limitComboBox.setCurrentIndex(focusedConstraint.validationMode.value)
        self.limitSpinBox.setValue(focusedConstraint.limit)
        self.pageSpinBox.setValue(focusedConstraint.page)
        self.sortedCheckBox.setChecked(focusedConstraint.sort)
        self.validateButton.setEnabled(focusedConstraint.implemented)
        self._loadViolations(focusedConstraint.tableName)

    def _updateFocusedConstraintLabel(self) -> None:
        constraint = self._model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        self.labelRight.setText(constraint.pretty())

    def _updateFocusedConstraintInputCount(self) -> None:
        constraint = self._model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        if constraint.inputCount != -1:
            self.inputRowsLabel.setText(f"Rows to check: {constraint.inputCount:,}")
        else:
            self.inputRowsLabel.setText(f"Rows to check: ?")

    def _changeLimitMode(self) -> None:
        if self.limitComboBox.currentIndex() == ValidationMode.NO_LIMIT.value:
            self.limitLabel.hide()
            self.limitSpinBox.hide()
            self.pageLabel.hide()
            self.pageSpinBox.hide()
            self.sortedCheckBox.hide()
        else:
            self.limitLabel.show()
            self.limitSpinBox.show()
            self.pageLabel.show()
            self.pageSpinBox.show()
            self.sortedCheckBox.show()

    def _changeLimitSorted(self) -> None:
        # Page should not be selectable if limiting random input
        self.pageSpinBox.setEnabled(self.sortedCheckBox.isChecked())
        self.pageLabel.setEnabled(self.sortedCheckBox.isChecked())
        self.pageSpinBox.setValue(1)

    def _validateAll(self) -> None:
        if not self._model.constraintCheckModel.validatingAll():
            self._model.constraintCheckModel.validateAll()
        else:
            self._model.constraintCheckModel.stopValidatingAll()
        self._updateValidateAllLabel()

    def _updateValidateAllLabel(self) -> None:
        self.validateAllButton.setText(
            "Stop Validating All"
            if self._model.constraintCheckModel.validatingAll()
            else "Validate All"
        )

    def _startValidation(self) -> None:
        limitMode = ValidationMode(self.limitComboBox.currentIndex())
        sort = self.sortedCheckBox.isChecked()
        limit = self.limitSpinBox.value()
        page = self.pageSpinBox.value()
        self._model.constraintCheckModel.validateFocusedConstraint(
            limitMode, limit, page, sort
        )

    def _loadViolations(self, table: str) -> None:
        constraint = self._model.constraintCheckModel.focusedConstraint
        if not constraint or constraint.tableName != table:
            return
        self.violationsTableModel.setTable(table)
        self.violationsTableModel.select()
        self.violationsTableView.hideColumn(0)
        headerResizeNeatly(self.violationsTableView.horizontalHeader())

        self._updateViolationsLabel(constraint)
        self.exportButton.setEnabled(constraint.violations is not None)

    def _updateViolationsLabel(self, constraint: Constraint) -> None:
        if constraint.violations is None:
            self.violationsLabel.setText("Not Validated")
            return

        violationsCount = len(constraint.violations) - 1
        hiddenCount = (
            len(constraint.hiddenViolations) - 1 if constraint.hiddenViolations else 0
        )
        violationCountText = (
            f"{violationsCount} violation{"s" if violationsCount != 1 else ""} found"
        )
        exceptionCountText = (
            f" ({hiddenCount} exception{"s" if hiddenCount != 1 else ""} hidden)"
            if hiddenCount
            else ""
        )
        self.violationsLabel.setText(f"{violationCountText}{exceptionCountText}.")

    def _exportSingleConstraint(self) -> None:
        constraint = self._model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        defaultFileName = f"constraint_violations_{constraint.property.identifier}_{constraint.identifier}"
        if constraint.validationState == ValidationState.PARTIAL:
            defaultFileName += "_partial"
        fileName, fileFilter = QFileDialog.getSaveFileName(
            self,
            f"Export Violations for {constraint.property.identifier}-{constraint.identifier}",
            f"{self._exportDir}/{defaultFileName}",
            "Excel Workbook (*.xlsx);;ODF Spreadsheet (*.ods)",
        )
        if not fileName:
            return
        if fileFilter == "ODF Spreadsheet (*.ods)":
            if not fileName.endswith(".ods"):
                fileName += ".ods"
        else:
            if not fileName.endswith(".xlsx"):
                fileName += ".xlsx"
        self._exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportUrlCheckBox.isChecked()
        self._exporter.exportSingleConstraint(constraint, fileName, exportUrl)

    def _exportAll(self) -> None:
        validatedConstraints = sorted(
            [
                c
                for c in self._model.constraintCheckModel.constraints
                if c.validationState
                in [ValidationState.VALIDATED, ValidationState.PARTIAL]
            ]
        )
        defaultFileName = "constraint_violations_combined"
        fileName, fileFilter = QFileDialog.getSaveFileName(
            self,
            "Export Violations for All Validated Constraints",
            f"{self._exportDir}/{defaultFileName}",
            "Excel Workbook (*.xlsx);;ODF Spreadsheet (*.ods)",
        )
        if not fileName:
            return
        if fileFilter == "ODF Spreadsheet (*.ods)":
            if not fileName.endswith(".ods"):
                fileName += ".ods"
        else:
            if not fileName.endswith(".xlsx"):
                fileName += ".xlsx"
        self._exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportAllUrlCheckBox.isChecked()
        self._exporter.exportMultipleConstraints(
            validatedConstraints, fileName, exportUrl
        )

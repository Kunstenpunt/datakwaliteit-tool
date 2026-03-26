from PySide6.QtCore import (
    QFileInfo,
    QModelIndex,
    QSortFilterProxyModel,
    QStandardPaths,
)
from PySide6.QtWidgets import QFileDialog, QWidget

from ..backend.constraint.base import Constraint, ValidationMode, ValidationState
from ..backend.export import Exporter
from ..backend.model import Model

from .designer.constrainttab import Ui_ConstraintTab
from .simpletablemodel import (
    headerResizeNeatly,
    SimpleTableModel,
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
        self.propertiesTableView.doubleClicked.connect(
            self._tableClickHandler.onTableDoubleClicked
        )
        self.violationsTableView.doubleClicked.connect(
            self._tableClickHandler.onTableDoubleClicked
        )
        self._model.constraintCheckModel.constraintsUpdated.connect(
            self._onConstraintsUpdated
        )
        self._model.constraintCheckModel.validationStateChanged.connect(
            self._onValidationStateChanged
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
        self._model.constraintCheckModel.focusedConstraintViolationsUpdated.connect(
            self._updateViolations
        )
        self._model.constraintCheckModel.validateAllDone.connect(
            self._updateValidateAllLabel
        )

    def _updateConstraints(self) -> None:
        self._model.constraintCheckModel.updateConstraints()

    def _onConstraintsUpdated(self) -> None:
        headerLabels = [
            "Prop ID",
            "Prop label",
            "Constraint ID",
            "Constraint Label",
            "Implemented",
            "Validated",
        ]
        table = [
            headerLabels
        ] + self._model.constraintCheckModel.getConstraintsListFull()
        sortableModel = QSortFilterProxyModel()
        sortableModel.setSourceModel(SimpleTableModel(table))
        self.propertiesTableView.setModel(sortableModel)
        header = self.propertiesTableView.horizontalHeader()
        headerResizeNeatly(header)
        self.propertiesTableView.selectionModel().currentChanged.connect(
            self._onPropertySelectionChanged
        )
        if len(table) > 1:
            self.propertiesTableView.selectRow(0)

    def _onValidationStateChanged(self) -> None:
        data = self._model.constraintCheckModel.getConstraintsListFull()
        model = self.propertiesTableView.model()
        if not isinstance(model, QSortFilterProxyModel):
            return
        sourceModel = model.sourceModel()
        validatedColumnIndex = 5
        for rowIndex, row in enumerate(data):
            sourceModel.setData(
                sourceModel.index(rowIndex, validatedColumnIndex), row[5]
            )

    def _onPropertySelectionChanged(self, current: QModelIndex, _: QModelIndex) -> None:
        if current == None:
            return
        tableModel = current.model()
        propId = tableModel.data(tableModel.index(current.row(), 0))
        constraintId = tableModel.data(tableModel.index(current.row(), 2))
        self._model.constraintCheckModel.setFocusedConstraint(propId, constraintId)

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
        self._updateViolations()

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

    def _updateViolations(self) -> None:
        constraint = self._model.constraintCheckModel.focusedConstraint
        if not constraint:
            return

        self.violationsTableView.updateViolations(constraint)
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
                for c in self._model.constraintCheckModel.constraints.values()
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

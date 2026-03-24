from PySide6.QtCore import (
    QFileInfo,
    QModelIndex,
    QSortFilterProxyModel,
    QStandardPaths,
)
from PySide6.QtWidgets import QFileDialog, QWidget

from ..backend.constraint.base import ValidationMode, ValidationState
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

        self.model = model
        self.exporter = Exporter(self.model.wikibaseConfig)
        self.exportDir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation,
        )
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.validateButton.setEnabled(False)
        self.exportButton.setEnabled(False)

        self.reloadButton.clicked.connect(self.updateConstraints)
        self.validateAllButton.clicked.connect(self.validateAll)
        self.validateButton.clicked.connect(self.onValidateButtonClicked)
        self.exportAllButton.clicked.connect(self.exportAllValidated)
        self.exportButton.clicked.connect(self.exportSingleConstraint)
        self.limitComboBox.currentIndexChanged.connect(self.changeLimitMode)
        self.changeLimitMode()
        self.sortedCheckBox.checkStateChanged.connect(self.changeLimitSorted)
        self.changeLimitSorted()
        self.tableClickHandler = TableClickHandler(self.model.wikibaseConfig)
        self.propertiesTableView.doubleClicked.connect(
            self.tableClickHandler.onTableDoubleClicked
        )
        self.violationsTableView.doubleClicked.connect(
            self.tableClickHandler.onTableDoubleClicked
        )
        self.model.constraintCheckModel.constrainedPropertiesUpdated.connect(
            self.onConstrainedPropertiesUpdated
        )
        self.model.constraintCheckModel.constrainedPropertyValidationStateChanged.connect(
            self.onConstrainedPropertyValidationStateChanged
        )
        self.model.constraintCheckModel.focusedPropertyConstraintUpdated.connect(
            self.onFocusedPropertyConstraintUpdated
        )
        self.model.constraintCheckModel.focusedPropertyConstraintInputCountUpdated.connect(
            self.updateFocusedPropertyConstraintInputCount
        )
        self.model.constraintCheckModel.focusedPropertyConstraintQualifiersUpdated.connect(
            self.updateFocusedPropertyConstraintLabel
        )
        self.model.constraintCheckModel.focusedPropertyConstraintViolationsUpdated.connect(
            self.updateViolationsTableView
        )
        self.model.constraintCheckModel.validateAllDone.connect(
            self.updateValidateAllLabel
        )

    def updateConstraints(self) -> None:
        self.model.constraintCheckModel.updateConstraints()

    def onConstrainedPropertiesUpdated(self) -> None:
        headerLabels = [
            "Prop ID",
            "Prop label",
            "Constraint ID",
            "Constraint Label",
            "Implemented",
            "Validated",
        ]
        data = [headerLabels] + self.model.constraintCheckModel.getConstraintsListFull()
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.propertiesTableView.setModel(sortableDataModel)
        header = self.propertiesTableView.horizontalHeader()
        headerResizeNeatly(header)
        self.propertiesTableView.selectionModel().currentChanged.connect(
            self.onPropertySelectionChanged
        )
        if len(data) > 1:
            self.propertiesTableView.selectRow(0)

    def onConstrainedPropertyValidationStateChanged(self) -> None:
        data = self.model.constraintCheckModel.getConstraintsListFull()
        model = self.propertiesTableView.model()
        if not isinstance(model, QSortFilterProxyModel):
            return
        sourceModel = model.sourceModel()
        validatedColumnIndex = 5
        for rowIndex, row in enumerate(data):
            sourceModel.setData(
                sourceModel.index(rowIndex, validatedColumnIndex), row[5]
            )

    def onPropertySelectionChanged(self, current: QModelIndex, _: QModelIndex) -> None:
        if current == None:
            return
        tableModel = current.model()
        propId = tableModel.data(tableModel.index(current.row(), 0))
        constraintId = tableModel.data(tableModel.index(current.row(), 2))
        self.model.constraintCheckModel.setFocusedConstraint(propId, constraintId)

    def onFocusedPropertyConstraintUpdated(self) -> None:
        focusedPropertyConstraint = self.model.constraintCheckModel.focusedConstraint
        if not focusedPropertyConstraint:
            return
        self.updateFocusedPropertyConstraintLabel()
        self.updateFocusedPropertyConstraintInputCount()
        self.limitComboBox.setCurrentIndex(
            focusedPropertyConstraint.validationMode.value
        )
        self.limitSpinBox.setValue(focusedPropertyConstraint.limit)
        self.pageSpinBox.setValue(focusedPropertyConstraint.page)
        self.sortedCheckBox.setChecked(focusedPropertyConstraint.sort)
        self.validateButton.setEnabled(focusedPropertyConstraint.implemented)
        self.updateViolationsTableView()

    def updateFocusedPropertyConstraintLabel(self) -> None:
        constraint = self.model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        self.labelRight.setText(constraint.pretty())

    def updateFocusedPropertyConstraintInputCount(self) -> None:
        constraint = self.model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        if constraint.inputCount != -1:
            self.inputRowsLabel.setText(f"Rows to check: {constraint.inputCount:,}")
        else:
            self.inputRowsLabel.setText(f"Rows to check: ?")

    def changeLimitMode(self) -> None:
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

    def changeLimitSorted(self) -> None:
        # Page should not be selectable if limiting random input
        self.pageSpinBox.setEnabled(self.sortedCheckBox.isChecked())
        self.pageLabel.setEnabled(self.sortedCheckBox.isChecked())
        self.pageSpinBox.setValue(1)

    def validateAll(self) -> None:
        if not self.model.constraintCheckModel.validatingAll():
            self.model.constraintCheckModel.validateAll()
        else:
            self.model.constraintCheckModel.stopValidatingAll()
        self.updateValidateAllLabel()

    def updateValidateAllLabel(self) -> None:
        self.validateAllButton.setText(
            "Stop Validating All"
            if self.model.constraintCheckModel.validatingAll()
            else "Validate All"
        )

    def onValidateButtonClicked(self) -> None:
        limitMode = ValidationMode(self.limitComboBox.currentIndex())
        sort = self.sortedCheckBox.isChecked()
        limit = self.limitSpinBox.value()
        page = self.pageSpinBox.value()
        self.model.constraintCheckModel.validateFocusedConstraint(
            limitMode, limit, page, sort
        )

    def updateViolationsTableView(self) -> None:
        constraint = self.model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        data = constraint.violations
        self.exportButton.setEnabled(data != None)
        if data == None:
            self.violationsTableView.setModel(None)
            self.violationsLabel.setText("Not Validated")
            return
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.violationsTableView.setModel(sortableDataModel)
        header = self.violationsTableView.horizontalHeader()
        headerResizeNeatly(header)
        header.resizeSection(0, header.defaultSectionSize())
        violations = len(data) - 1
        self.violationsLabel.setText(
            f"{violations} violation{"s" if violations != 1 else ""} found."
        )

    def exportSingleConstraint(self) -> None:
        constraint = self.model.constraintCheckModel.focusedConstraint
        if not constraint:
            return
        defaultFileName = f"constraint_violations_{constraint.property.identifier}_{constraint.identifier}"
        if constraint.validationState == ValidationState.PARTIAL:
            defaultFileName += "_partial"
        fileName, fileFilter = QFileDialog.getSaveFileName(
            self,
            f"Export Violations for {constraint.property.identifier}-{constraint.identifier}",
            f"{self.exportDir}/{defaultFileName}",
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
        self.exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportUrlCheckBox.isChecked()
        self.exporter.exportSingleConstraint(constraint, fileName, exportUrl)

    def exportAllValidated(self) -> None:
        validatedConstraints = sorted(
            [
                c
                for c in self.model.constraintCheckModel.constraints.values()
                if c.validationState
                in [ValidationState.VALIDATED, ValidationState.PARTIAL]
            ]
        )
        defaultFileName = "constraint_violations_combined"
        fileName, fileFilter = QFileDialog.getSaveFileName(
            self,
            "Export Violations for All Validated Constraints",
            f"{self.exportDir}/{defaultFileName}",
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
        self.exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportAllUrlCheckBox.isChecked()
        self.exporter.exportMultipleConstraints(
            validatedConstraints, fileName, exportUrl
        )

from collections import OrderedDict

from pyexcel_ods3 import save_data as saveData

from .wikibasehelper import BASE_URL
from .utils import urlFromId


def exportSingleConstraintToOds(constraint, fileName, exportUrl):
    sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
    sheetData = constraint.violations
    if exportUrl:
        sheetData = [
            [urlFromId(el, BASE_URL) if urlFromId(el, BASE_URL) else el for el in row]
            for row in sheetData
        ]
    data = OrderedDict()
    data.update({sheetName: sheetData})
    saveData(fileName, data)

# -*- coding: utf-8 -*-

"""
Effect : Size
"""

from Framework.Utils.Units import Units
from Framework.Utils.ParamType.ParamTypeBase import ParamTypeBase
from Framework.Exception import ATException


class Size(ParamTypeBase):
    """Size
    """
    def __init__(self, typeAndValidation):
        super(Size, self).__init__(typeAndValidation)
        self.minSize = None
        self.maxSize = None
        self.smallerUnit = None
        if self.validation is None:
            return
        if 'min' in self.validation['min']:
            self.minSize = self.validation['min']
        if (self.minSize is not None) and (not Units.isSize(self.minSize)):
            raise ATException('Size object create failed, the value of min[%s] is not size type.' % self.minSize)

        if 'max' in self.validation['max']:
            self.maxSize = self.validation['max']
        if (self.maxSize is not None) and (not Units.isSize(self.maxSize)):
            raise ATException('Size object create failed, the value of min[%s] is not size type.' % self.minSize)

        self.minSizeNum = Units.getNumber(self.minSize)
        self.maxSizeNum = Units.getNumber(self.maxSize)

        if self.maxSizeNum and self.minSizeNum and \
            (Units.getUnit(self.maxSize)) != (Units.getUnit(self.minSize)):
            self.minSizeNum, self.maxSizeNum, self.smallerUnit = Units._baseMath(self.minSize, self.maxSize)

        if self.minSizeNum and self.maxSizeNum and self.minSizeNum > self.maxSizeNum:
            raise ATException('Size object create failed, value of max[%s] < min[%s].' % (self.maxSize, self.minSize))

    def hasValidation(self):
        """
        """
        if self.validation:
            return True
        return False

    def getValidation(self):
        """
        """
        if self.hasValidation():
            return self.validation
        return None

    def getValidInput(self, defauled):
        """validate and return
        """
        if defauled == 'None' or defauled is None:
            return None
        if not Units.isSize(defauled):
            raise ATException('Size object getValidInput() failed, defauled[%s] is not size type.' % defauled)
        if self.minSize is None and self.maxSize is None:
            return defauled

        if self.smallerUnit:
            sizeNumber = Units.getNumber(Units.convert(defauled, self.smallerUnit))
            if self.minSizeNum <= sizeNumber <= self.maxSizeNum:
                return defauled
            raise ATException('Size object getValidInput() failed, defauled[%s] out of range or has different units.' % defauled)
        else:
            sizeNumber = Units.getNumber(defauled)

        if self.minSize is None and self.maxSize is not None:
            if sizeNumber > self.maxSizeNum:
                raise ATException('Size object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.maxSize))
            elif Units.getUnit(defauled) != Units.getUnit(self.maxSize):
                defauledNum, maxSizeNum, unit = Units._baseMath(defauled, self.maxSize)
                if defauledNum > maxSizeNum:
                    raise ATException('Size object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.maxSize))
            return defauled

        if self.minSize is not None and self.maxSize is None:
            if sizeNumber < self.maxSizeNum:
                raise ATException('Size object getValidInput() failed, defauled[%s] < min[%s].' % (defauled, self.minSize))
            elif Units.getUnit(defauled) != Units.getUnit(self.maxSize):
                defauledNum, minSizeNum, unit = Units._baseMath(defauled, self.minSize)
                if defauledNum < minSizeNum:
                    raise ATException('Size object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.minSize))
            return defauled

        if Units.getUnit(self.maxSize) == Units.getUnit(self.minSize) and Units.getUnit(defauled) != Units.getUnit(self.minSize):
            sizeNumber = Units.getNumber(Units.convert(defauled, Units.getUnit(self.minSize)))
            if self.minSizeNum <= sizeNumber <= self.maxSizeNum:
                return defauled
        elif Units.getUnit(self.maxSize) == Units.getUnit(self.minSize) and Units.getUnit(defauled) == Units.getUnit(self.minSize):
            if self.minSizeNum <= sizeNumber <= self.maxSizeNum:
                return defauled
        raise ATException('Size object getValidInput() failed, defauled[%s] out of range or has different units.' % defauled)

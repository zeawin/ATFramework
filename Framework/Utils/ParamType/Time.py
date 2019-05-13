# -*- coding: utf-8 -*-

"""
Effect : methods deal with time, return the instance
"""

from Framework.Utils.Units import Units
from Framework.Utils.ParamType.ParamTypeBase import ParamTypeBase
from Framework.Exception.ATException import ATException


class Time(ParamTypeBase):
    """Time
    """
    def __init__(self, typeValidation):
        super(Time, self).__init__(typeValidation)
        self.minTime = None
        self.maxTime = None
        self.smallerUnit = None
        if self.validation is None:
            return
        if 'min' in self.validation['min']:
            self.minTime = self.validation['min']
        if (self.minTime is not None) and (not Units.isTime(self.minTime)):
            raise ATException('Time object create failed, the value of min[%s] is not time type.' % self.minTime)

        if 'max' in self.validation['max']:
            self.maxTime = self.validation['max']
        if (self.maxTime is not None) and (not Units.isTime(self.maxTime)):
            raise ATException('Time object create failed, the value of min[%s] is not time type.' % self.minTime)

        self.minTimeNum = Units.getNumber(self.minTime)
        self.maxTimeNum = Units.getNumber(self.maxTime)

        if self.maxTimeNum and self.minTimeNum and \
            (Units.getUnit(self.maxTime)) != (Units.getUnit(self.minTime)):
            self.minTimeNum, self.maxTimeNum, self.smallerUnit = Units._baseMath(self.minTime, self.maxTime)

        if self.minTimeNum and self.maxTimeNum and self.minTimeNum > self.maxTimeNum:
            raise ATException('Time object create failed, value of max[%s] < min[%s].' % (self.maxTime, self.minTime))

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
        if not Units.isTime(defauled):
            raise ATException('Time object getValidInput() failed, defauled[%s] is not time type.' % defauled)
        if self.minTime is None and self.maxTime is None:
            return defauled

        if self.smallerUnit:
            timeNumber = Units.getNumber(Units.convert(defauled, self.smallerUnit))
            if self.minTimeNum <= timeNumber <= self.maxTimeNum:
                return defauled
            raise ATException('Time object getValidInput() failed, defauled[%s] out of range or has different units.' % defauled)
        else:
            timeNumber = Units.getNumber(defauled)

        if self.minTime is None and self.maxTime is not None:
            if timeNumber > self.maxTimeNum:
                raise ATException('Time object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.maxTime))
            elif Units.getUnit(defauled) != Units.getUnit(self.maxTime):
                defauledNum, maxTimeNum, unit = Units._baseMath(defauled, self.maxTime)
                if defauledNum > maxTimeNum:
                    raise ATException('Time object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.maxTime))
            return defauled

        if self.minTime is not None and self.maxTime is None:
            if timeNumber < self.maxTimeNum:
                raise ATException('Time object getValidInput() failed, defauled[%s] < min[%s].' % (defauled, self.minTime))
            elif Units.getUnit(defauled) != Units.getUnit(self.maxTime):
                defauledNum, minTimeNum, unit = Units._baseMath(defauled, self.minTime)
                if defauledNum < minTimeNum:
                    raise ATException('Time object getValidInput() failed, defauled[%s] > max[%s].' % (defauled, self.minTime))
            return defauled

        if Units.getUnit(self.maxTime) == Units.getUnit(self.minTime) and Units.getUnit(defauled) != Units.getUnit(self.minTime):
            timeNumber = Units.getNumber(Units.convert(defauled, Units.getUnit(self.minTime)))
            if self.minTimeNum <= timeNumber <= self.maxTimeNum:
                return defauled
        elif Units.getUnit(self.maxTime) == Units.getUnit(self.minTime) and Units.getUnit(defauled) == Units.getUnit(self.minTime):
            if self.minTimeNum <= timeNumber <= self.maxTimeNum:
                return defauled
        raise ATException('Time object getValidInput() failed, defauled[%s] out of range or has different units.' % defauled)
# -*- coding: utf-8 -*-

"""
    Effect: validate and return data
"""

import re

# define Size Units
BYTE = 'B'
KILOBYTE = 'KB'
MEGABYTE = 'MB'
GIGABYTE = 'GB'
TERABYTE = 'TB'
PETABYTE = 'PB'
BLOCK = 'BC'
PERCENT = '%'
SIZE_UNITS = [BLOCK, BYTE, KILOBYTE, MEGABYTE, GIGABYTE, TERABYTE, PETABYTE]

# define time units
MICROSECOND = 'US'
MILLISECOND = 'MS'
SECOND = 'S'
MINUTE = 'M'
HOUR = 'H'
DAY = 'D'
WEEK = 'WK'
MONTH = 'MO'
YEAR = 'YR'
TIME_UNITS = [MICROSECOND, MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, YEAR]

# a number value
NUMBER_REGEX = '^[+-]?(((\d+(\.\d*)?)|0\.\d+)([eE][+-]?[0-9]+)?)'

# percentage, time, and size regexp
PERCENTAGE_REGEX = '\d+(.\d+)?%$'
TIME_REGEX = NUMBER_REGEX+'('+'|'.join(TIME_UNITS)+')$'
SIZE_REGEX = NUMBER_REGEX+'('+'|'.join(SIZE_UNITS)+')$'
TIME_UNIT_REGEX = '^(' + '|'.join(TIME_UNITS) + ')$'
SIZE_UNIT_REGEX = '^(' + '|'.join(SIZE_UNITS) + ')$'

# size trans rule base on 'B'
ONE_K = 1024
ONE_BC = 512
ONE_MB = float(ONE_K * ONE_K)
ONE_GB = float(ONE_MB * ONE_K)
ONE_TB = float(ONE_GB * ONE_K)
ONE_PB = float(ONE_TB * ONE_K)

# time trans rule base on 'S'
ONE_US = float(1 / float(1000000))
ONE_MS = float(1 / float(1000))
ONE_M = 60
ONE_H = 60 * ONE_M
ONE_D = 24 * ONE_H
ONE_WK = 7 * ONE_D
ONE_MO = 30 * ONE_D
ONE_YR = float(365 * ONE_D)


class Units:
    """Units
    """
    def __init__(self):
        pass

    @classmethod
    def isPercentage(cls, value):
        """To judge whether the data as a percentage
        """
        return re.match(PERCENTAGE_REGEX, value) is not None

    @classmethod
    def isTime(cls, value):
        """To judge whether the data as a time
        """
        return re.match(str(TIME_REGEX), str(value), re.I) is not None

    @classmethod
    def isSize(cls, value):
        """To judge whether the data as a size
        """
        return re.match(str(SIZE_REGEX), str(value), re.I) is not None

    @classmethod
    def isNumber(cls, value):
        """To judge whether the data as a size
        """
        numberFlag = False
        if isinstance(value, str):
            if re.match('^'+str(NUMBER_REGEX)+'$', value):
                numberFlag = True
        return  isinstance(value, int) or isinstance(value, float) or isinstance(value, long) or numberFlag

    @classmethod
    def getNumber(cls, value):
        """get the number from data with unit
        """
        if value is None:
            return None
        if Units.isNumber(value):
            return float(value)
        if Units.isTime(value) or Units.isSize(value) or Units.isPercentage(value):
            values = float(re.sub('[a-zA-Z%]*$', '', str(value)))
            return values

        raise Exception('getNumber() failed, input value: [%s] is invalid.' % value)

    @classmethod
    def getUnit(cls, value):
        """get the unit from data with unit
        """
        if Units.isTime(value) or Units.isSize(value):
            unit = re.sub(str(NUMBER_REGEX), '', value)
            return unit

        raise Exception('getUnit() failed, input value: [%s] is invalid.' % value)

    @classmethod
    def convert(cls, value, unit):
        """To trans the value to a specified value with unit
        """
        if Units.isTime(value) and re.match(str(TIME_UNIT_REGEX), str(unit), re.I):
            rate = Units.__rate(Units.getUnit(value), unit)
            return str(rate * Units.getNumber(value)) + unit
        elif Units.isSize(value) and re.match(str(SIZE_UNIT_REGEX), str(unit), re.I):
            rate = Units.__rate(Units.getUnit(value), unit)
            return str(rate * Units.getNumber(value)) + unit

    @staticmethod
    def __rate(fromUnit, toUnit):
        """calculate the rate from fromUnit to toUnit
        """
        if not isinstance(fromUnit, str) or not isinstance(toUnit, str):
            raise Exception('convert units failed, parameter invalid.')
        fromUnit = fromUnit.upper()
        toUnit = toUnit.upper()

        #size rate
        sizeBaseRate = {
            BYTE: 1,
            BLOCK: ONE_BC,
            KILOBYTE: ONE_K,
            MEGABYTE: ONE_MB,
            GIGABYTE: ONE_GB,
            TERABYTE: ONE_TB,
            PETABYTE: ONE_PB
        }
        # time rate
        timeBaseRate = {
            MICROSECOND: ONE_US,
            MILLISECOND: ONE_MS,
            SECOND: 1,
            MINUTE: ONE_M,
            HOUR: ONE_H,
            DAY: ONE_D,
            WEEK: ONE_WK,
            MONTH: ONE_MO,
            YEAR: ONE_YR
        }

        if re.match(str(TIME_UNIT_REGEX), str(fromUnit), re.I) \
            and re.match(str(TIME_UNIT_REGEX), str(toUnit), re.I):
            fromUnitRate = timeBaseRate.get(fromUnit, 0)
            toUnitRate = timeBaseRate.get(toUnit, 0)
            return float(float(fromUnitRate) / float(toUnitRate))

        elif re.match(str(SIZE_UNIT_REGEX), str(fromUnit), re.I) \
            and re.match(str(SIZE_UNIT_REGEX), str(toUnit), re.I):
            fromUnitRate = sizeBaseRate.get(fromUnit, 0)
            toUnitRate = sizeBaseRate.get(toUnit, 0)
            return float(float(fromUnitRate) / float(toUnitRate))
        else:
            raise Exception('[%s] and [%s] are not same type.' % (fromUnit, toUnit))

    @classmethod
    def subtract(cls, maxValue, minVlaue):
        """Calculate two numerical value with unit of the difference
        """
        numMaxValue, numMinValue, unit = Units._baseMath(maxValue, minVlaue)
        total = numMaxValue - numMinValue
        return str(total) + unit

    @classmethod
    def _baseMath(cls, valueA, valueB):
        """Calculae two data with units
        """
        numValueA, unitValueA = Units.parse(valueA)
        numValueB, unitValueB = Units.parse(valueB)

        if unitValueB == unitValueA:
            return numValueA, numValueB, unitValueA
        else:
            unit = Units.getSmallerUnit(unitValueA, unitValueB)
            numValueA = Units.getNumber(Units.convert(valueA, unit))
            numValueB = Units.getNumber(Units.convert(valueB, unit))
            return numValueA, numValueB, unit

    @classmethod
    def getSmallerUnit(cls, unitA, unitB):
        """
        """
        if unitA == unitB:
            return unitA
        elif unitA in SIZE_UNITS and unitB in SIZE_UNITS:
            for unit in SIZE_UNITS:
                if unit == unitA:
                    return unitA
                elif unit == unitB:
                    return unitB
        elif unitA in TIME_UNITS and unitB in TIME_UNITS:
            for unit in TIME_UNITS:
                if unit == unitA:
                    return unitA
                elif unit == unitB:
                    return unitB
        elif unitA == PERCENT and unitB == PERCENT:
            return PERCENT
        raise Exception('The provided units are not valid, [%s] and [%s]' % (unitA, unitB))

    @classmethod
    def getLargerUnit(cls, unitA, unitB):
        """
        """
        if unitA == unitB:
            return unitA
        elif unitA in SIZE_UNITS and unitB in SIZE_UNITS:
            for unit in SIZE_UNITS:
                if unit == unitA:
                    return unitB
                elif unit == unitB:
                    return unitA
        elif unitA in TIME_UNITS and unitB in TIME_UNITS:
            for unit in TIME_UNITS:
                if unit == unitA:
                    return unitB
                elif unit == unitB:
                    return unitB
        elif unitA == PERCENT and unitB == PERCENT:
            return PERCENT
        raise Exception('The provided units are not valid, [%s] and [%s]' % (unitA, unitB))

    @classmethod
    def parse(cls, value):
        """Access to data with unit values and units
        """
        err = '%s dose not appear to be in units format.' % value
        num, unit = None, None
        if not Units.isSize(value) and not Units.isTime(value) and not Units.isPercentage(value):
            raise Exception(err)
        matchUnit = re.match(str(NUMBER_REGEX)+'(\S+)', value)
        if matchUnit:
            num = float(matchUnit.group(1))
            unit = matchUnit.group(6)
        else:
            raise Exception(err)

        return num, unit

    @staticmethod
    def _compare(unitType, valueA, valueB):
        """Compare the two data
        """
        if re.match('percentage|size|time', unitType.lower()):
            numVlaueA, numVlaueB, unit = Units._baseMath(valueA, valueB)
            return numVlaueA - numVlaueB
        else:
            raise Exception('Type: [%s] is invalid.' % unitType)

    @classmethod
    def comparePercentage(cls, valueA, valueB):
        """
        """
        if Units.isPercentage(valueA) and Units.isPercentage(valueB):
            return Units._compare('percentage', valueA, valueB)
        else:
            raise Exception(' neither valueA nor valueB is not percentage or both.')

    @classmethod
    def compareSize(cls, valueA, valueB):
        """
        """
        if Units.isSize(valueA) and Units.isSize(valueB):
            return Units._compare('size', valueA, valueB)
        else:
            raise Exception(' neither valueA nor valueB is not size or both.')

    @classmethod
    def compareTime(cls, valueA, valueB):
        """
        """
        if Units.isTime(valueA) and Units.isTime(valueB):
            return Units._compare('time', valueA, valueB)
        else:
            raise Exception('Neither valueA nor valueB is not time or both.')

    @classmethod
    def sum(cls, valueA, valueB):
        """
        """
        numMaxValue, numMinValue, unit = Units._baseMath(valueA, valueB)
        total = numMaxValue + numMinValue
        return str(total) + unit

    @classmethod
    def divide(cls, value, number):
        """
        """
        if isinstance(value, str) and (isinstance(number, int) or isinstance(number, float)):
            valueA, unit = Units.parse(value)
            total = float(valueA / number)
            return str(total) + unit
        else:
            raise Exception('Units.divide() input param invalid.')
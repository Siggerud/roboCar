def map_value_to_new_scale(inputValue, newScaleMinValue, newScaleMaxValue, valuePrecision, oldScaleMinValue=-1, oldScaleMaxValue=1):
    newScaleSpan = newScaleMaxValue - newScaleMinValue
    oldScaleSpan = oldScaleMaxValue - oldScaleMinValue

    valueScaled = float(inputValue - oldScaleMinValue) / float(oldScaleSpan)
    valueMapped = round(newScaleMinValue + (valueScaled * newScaleSpan), valuePrecision)

    return valueMapped

def round_nearest(x, a):
    return round(x / a) * a
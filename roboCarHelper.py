def scale_button_press_value(pressValue, pwmMinValue, pwmMaxValue, valuePrecision, buttonMinValue=-1, buttonMaxValue=1):
    pwmSpan = pwmMaxValue - pwmMinValue
    buttonSpan = buttonMaxValue - buttonMinValue

    valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)
    valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), valuePrecision)

    return valueMapped

def _round_nearest(self, x, a):
    return round(x / a) * a
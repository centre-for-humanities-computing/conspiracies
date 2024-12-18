import React, { useEffect, useMemo, useState } from "react";
import MultiRangeSlider from "multi-range-slider-react";

interface LogarithmicRangeSliderProps {
  min: number; // Real-world minimum value
  max: number; // Real-world maximum value
  minValue: number; // Current minimum value
  maxValue: number; // Current maximum value
  onChange: (values: { minValue: number; maxValue: number }) => void; // Callback for value changes
  style?: React.CSSProperties; // Optional style prop
  ruler?: boolean; // Optional ruler prop
}

const linearToLog = (
  value: number,
  minLinear: number,
  maxLinear: number,
  minLog: number,
  maxLog: number,
): number => {
  const clampedValue = Math.max(minLinear, Math.min(value, maxLinear));
  const linearRange = maxLinear - minLinear;
  const logRange = Math.log(maxLog) - Math.log(minLog);
  const logValue =
    Math.log(minLog) + ((clampedValue - minLinear) / linearRange) * logRange;
  return Math.exp(logValue);
};

const logToLinear = (
  value: number,
  minLinear: number,
  maxLinear: number,
  minLog: number,
  maxLog: number,
): number => {
  const clampedValue = Math.max(minLog, Math.min(value, maxLog));
  const linearRange = maxLinear - minLinear;
  const logRange = Math.log(maxLog) - Math.log(minLog);
  const logValue = Math.log(clampedValue);
  return minLinear + ((logValue - Math.log(minLog)) / logRange) * linearRange;
};

const LogarithmicRangeSlider: React.FC<LogarithmicRangeSliderProps> = ({
  min,
  max,
  minValue,
  maxValue,
  onChange,
  ruler,
  ...rest
}) => {
  const [minCaption, setMinCaption] = useState(Math.round(minValue));
  const [maxCaption, setMaxCaption] = useState(Math.round(maxValue));
  useEffect(() => {
    setMinCaption(minValue);
    setMaxCaption(maxValue);
  }, [minValue, maxValue]);

  // Slider operates on a linear scale
  const linearMin = 0;
  const linearMax = 100;
  const realValueToLinearScale = useMemo(() => {
    return (realValue: number) =>
      Math.round(logToLinear(realValue, linearMin, linearMax, min, max));
  }, [min, max]);
  const linearScaleToRealValue = useMemo(() => {
    return (linearScaleValue: number) =>
      Math.round(linearToLog(linearScaleValue, linearMin, linearMax, min, max));
  }, [min, max]);

  const handleSliderInput = (e: { minValue: number; maxValue: number }) => {
    const realMinValue = linearScaleToRealValue(e.minValue);
    const realMaxValue = linearScaleToRealValue(e.maxValue);
    setMinCaption(realMinValue);
    setMaxCaption(realMaxValue);
  };
  const handleSliderChange = (e: { minValue: number; maxValue: number }) => {
    const realMinValue = linearScaleToRealValue(e.minValue);
    const realMaxValue = linearScaleToRealValue(e.maxValue);
    onChange({ minValue: realMinValue, maxValue: realMaxValue });
  };

  const labels = [
    String(min),
    String(linearScaleToRealValue(25)),
    String(linearScaleToRealValue(50)),
    String(linearScaleToRealValue(75)),
    String(max),
  ];

  return (
    <MultiRangeSlider
      min={linearMin}
      max={linearMax}
      minValue={realValueToLinearScale(minValue)}
      maxValue={realValueToLinearScale(maxValue)}
      onInput={handleSliderInput}
      onChange={handleSliderChange}
      minCaption={String(minCaption)} // Use the updated caption state
      maxCaption={String(maxCaption)} // Use the updated caption state
      labels={labels}
      {...rest}
      ruler={ruler || false}
    />
  );
};
export default LogarithmicRangeSlider;

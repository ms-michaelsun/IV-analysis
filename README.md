# IV-analysis-dark

Simple python script with GUI to load and analyze devices dark IV curve, leveraging scipy library.

It extract R series and R shunt from the curve and then model the curve based on a simplify one-diode equation to obtained dark saturation current (J0) and ideality factor (n) minimizing rmse.

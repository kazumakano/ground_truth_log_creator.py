# config
This is directory for config files.
Put your config files here.
Config file must contain following parameters:
| Key   | Description                                  | Notes                              | Type        |
| ---   | ---                                          | ---                                | ---         |
| begin | datetime corresponding to 0 [s]              | must be like 'yyyy-mm-dd hh:mm:ss' | `str`       |
| freq  | frequency of ground truth position logs [Hz] | disabled if 0                      | `float`     |

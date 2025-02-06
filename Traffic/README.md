# Python CICFlowMeter

> This project is the modified version of [Python Wrapper CICflowmeter](https://gitlab.com/hieulw/cicflowmeter) and customized to fit our need with extra feature (Slow HTTP Detect).

### Environment
Ubuntu 22.04 LTS

### Installation
```sh
git clone https://github.com/YUANWRLD/CICFlowMeter.git
cd CICFlowMeter
python3 setup.py install
```

### Usage
```sh
usage: cicflowmeter [-h] (-i INPUT_INTERFACE | -f INPUT_FILE) [-t LIMIT] (-c | -m) output

positional arguments:
  output                output file name (in flow mode) or load predict model (in predict mode)

options:
  -h, --help            show this help message and exit
  -i INPUT_INTERFACE, --interface INPUT_INTERFACE
                        capture online data from INPUT_INTERFACE
  -f INPUT_FILE, --file INPUT_FILE
                        capture offline data from INPUT_FILE
  -t LIMIT, --timelimit LIMIT
                        the specified capture time (default is 10 mins)
  -c, --csv, --flow     output flows as csv
  -m, --mod             model used to predict the flow is benign or malicious
```

Convert pcap file to flow csv:

```
cicflowmeter -f example.pcap -c flows.csv
```

Sniff packets real-time from interface to flow csv: (**need root permission**)

```
cicflowmeter -i eth0 -c flows.csv
```

Predict the flows from pcap file with trained model: (**time limit argument is useless**)

```
cicflowmeter -f example.pcap -m model.pickle
```

Predict the flows real-time from interface with trained model: (**need root permission**)

```
cicflowmeter -i eth0 -m model.pickle
```

You can also specify the time limit (default:600 sec) you want to keep predicting: (**need root permission**)

```
cicflowmeter -i eth0 -t timelimit -m model.pickle
```

### Model training
We use the default Apache2 as the victim server and slowhttptest as the attack tool to collect pcap files for model training, you can train your own model to satisfy your server's configuration.

- Reference: https://www.unb.ca/cic/research/applications.html#CICFlowMeter

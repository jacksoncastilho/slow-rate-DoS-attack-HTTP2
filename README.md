# Slow Rate HTTP2 DoS PoC

PoC of five Slow Rate HTTP/2 DoS attacks seen in the following research paper:

[Nikhil Tripathi and Neminath Hubballi. Slow rate denial of service attacks against http/2 and detection. *Comput. Secur.*, 72(C):255–272, January 2018.](https://www.sciencedirect.com/science/article/pii/S0167404817301980)

The tool measures the connection waiting time at the web server for the specified attack payload.

### Prerequisites

You will need Python3 with the [Hyper-h2](https://python-hyper.org/h2/en/stable/index.html) dependency:

```
pip3 install h2
```

### Run

```
Usage:
    python slowrateDoSattackcompletePOSTheader.py --target <hostname> --port <port> --path <path> --process <number_of_processes> --delay <delay_time>

Arguments:
    -t, --target   : Target hostname or IP address (required)
    -p, --port     : Target port (default: 80)
    --path         : Target path (default: "/")
    -P, --process  : Number of attack processes to spawn (default: 1)
    -d, --delay    : Delay between starting each process in seconds (default: 0.1)
```

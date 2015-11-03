#!/bin/bash

python prepare_partitions_data.py --disk sda > /tmp/partitioning_data.json
fa_partition --data_driver=generic_simple --input_data_file=/tmp/partitioning_data.json --debug --log-file=/var/log/fuel-agent.log

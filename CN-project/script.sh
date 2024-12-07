#!/bin/bash


PYTHON_SCRIPT=""


OUTPUT_FILE=""


if [[ ! -f $OUTPUT_FILE ]]; then

    echo "throughput,avg_latency,pdr,total_time" > $OUTPUT_FILE
fi


for i in {1..60}
do

    OUTPUT=$(python3 $PYTHON_SCRIPT)


    THROUGHPUT=""
    AVG_LATENCY=""
    PDR=""
    TOTAL_TIME=""


    while IFS= read -r line; do

        if [[ $line =~ throughput:\ ([0-9\.]+) ]]; then
            THROUGHPUT=${BASH_REMATCH[1]}
        fi


        if [[ $line =~ avg_latency:\ ([0-9\.eE+-]+) ]]; then
            AVG_LATENCY=${BASH_REMATCH[1]}
        fi


        if [[ $line =~ PDR:\ ([0-9\.]+) ]]; then
            PDR=${BASH_REMATCH[1]}
        fi
        
        if [[ $line =~ total_time:\ ([0-9\.eE+-]+) ]]; then
            TOTAL_TIME=${BASH_REMATCH[1]}
        fi
    done <<< "$OUTPUT"
    echo "Run #$i - Throughput: $THROUGHPUT, Avg Latency: $AVG_LATENCY, PDR: $PDR, Total Time: $TOTAL_TIME"

    echo "$THROUGHPUT,$AVG_LATENCY,$PDR,$TOTAL_TIME" >> $OUTPUT_FILE
done

echo "All outputs saved to $OUTPUT_FILE"


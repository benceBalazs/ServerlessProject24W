#! /usr/bin/env bash

set -e -x -u -o pipefail

SANITY_SLEEP=20s

function run_scenario() {
    SCEANRIO=$1
    LOAD_TEST_VARIANT=$2
    TF_CONFIG=$3

    RESULTDIR=$PWD/results/scenario-$SCEANRIO/

    mkdir -p $RESULTDIR

    terraform -chdir=tf plan -out=$TF_CONFIG.tfplan -var-file=./configs/$TF_CONFIG.tfvars
    terraform -chdir=tf apply $TF_CONFIG.tfplan

    sleep $SANITY_SLEEP

    pushd tests
    RESULTDIR=$RESULTDIR LOAD_TEST_VARIANT=$LOAD_TEST_VARIANT python load_test.py >$RESULTDIR/load_test.log
    popd

    sleep $SANITY_SLEEP

    pushd metrics
    RESULTDIR=$RESULTDIR python main.py >$RESULTDIR/metrics.log
    popd

    sleep $SANITY_SLEEP
}

# |        	   | low | mid | high |
# | ---------- | --- | --- | ---- |
# | simple 	   | S1  | S2  | S3   |
# | production | S4  | S5  | S6   |

run_scenario 1 simple low
run_scenario 2 simple mid
run_scenario 3 simple high
run_scenario 4 production low
run_scenario 5 production mid
run_scenario 6 production high

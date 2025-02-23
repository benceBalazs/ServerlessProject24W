#! /usr/bin/env bash

set -e -x -u -o pipefail

SANITY_SLEEP=60s

function run_scenario() {
    SCEANRIO=$1
    LOAD_TEST_VARIANT=$2
    TF_CONFIG=$3

    RESULTDIR=$PWD/results/scenario-$SCEANRIO/

    mkdir -p $RESULTDIR

    terraform -chdir=tf plan -out=$TF_CONFIG.tfplan -var-file=./configs/$TF_CONFIG.tfvars >$RESULTDIR/terraform_plan.log
    terraform -chdir=tf apply $TF_CONFIG.tfplan >$RESULTDIR/terraform_apply.log

    sleep $SANITY_SLEEP

    pushd tests
    RESULTDIR=$RESULTDIR LOAD_TEST_VARIANT=$LOAD_TEST_VARIANT python load_test.py >$RESULTDIR/load_test.log
    popd

    sleep $SANITY_SLEEP
    sleep $SANITY_SLEEP

    pushd metrics
    RESULTDIR=$RESULTDIR python fetch_data.py >$RESULTDIR/fetch_data.log
    RESULTDIR=$RESULTDIR python create_plots.py >$RESULTDIR/create_plots.log
    popd

    # sleep $SANITY_SLEEP
}

run_scenario 1 simple low
run_scenario 2 simple mid
run_scenario 3 simple high
run_scenario 4 production low
run_scenario 5 production mid
run_scenario 6 production high

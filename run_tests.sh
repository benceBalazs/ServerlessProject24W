#! /usr/bin/env bash

set -e -x -u -o pipefail

function run_scenario() {
    SCEANRIO=$1
    LOAD_TEST_VARIANT=$2
    TF_CONFIG=$3

    RESULTDIR=$PWD/results/scenario-$SCEANRIO/

    mkdir -p $RESULTDIR

    terraform -chdir=tf plan -out=$TF_CONFIG.tfplan -var-file=./configs/$TF_CONFIG.tfvars >$RESULTDIR/terraform_plan.log
    terraform -chdir=tf apply $TF_CONFIG.tfplan >$RESULTDIR/terraform_apply.log
    rm tf/$TF_CONFIG.tfplan

    sleep 60s # finish the deployment

    pushd tests
    RESULTDIR=$RESULTDIR LOAD_TEST_VARIANT=$LOAD_TEST_VARIANT python load_test.py >$RESULTDIR/load_test.log
    popd

    sleep 120s # wait for processing
    sleep 120s # wait for the metrics to be available

    pushd metrics
    RESULTDIR=$RESULTDIR python fetch_data.py >$RESULTDIR/fetch_data.log
    RESULTDIR=$RESULTDIR python create_plots.py >$RESULTDIR/create_plots.log
    popd
}

run_scenario 1 simple low
sleep 3m
run_scenario 2 simple mid
sleep 3m
run_scenario 3 simple high
sleep 3m
run_scenario 4 production low
sleep 3m
run_scenario 5 production mid
sleep 3m
run_scenario 6 production high

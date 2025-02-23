import csv
import os
import time
from datetime import datetime, timedelta, UTC
from google.cloud import monitoring_v3
import numpy as np
import pandas as pd

from defs import *


COLLECTION_WINDOW_MINUTES = 11

client = monitoring_v3.MetricServiceClient()
interval = monitoring_v3.TimeInterval(
    {
        "start_time": datetime.now(UTC) - timedelta(minutes=COLLECTION_WINDOW_MINUTES),
        "end_time": datetime.now(UTC),
    }
)


def active_instances():
    query = {
        "name": PROJECT_NAME,
        "filter": 'metric.type="cloudfunctions.googleapis.com/function/active_instances"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }

    result = client.list_time_series(query)

    with open(CSV_ACTIVE_INSTANCES, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "function_name", "active_instances"])
        for data in result:
            for point in data.points:
                timestamp = point.interval.start_time
                value = point.value.int64_value
                writer.writerow(
                    [timestamp, data.resource.labels["function_name"], value]
                )


def memory_usages():
    query = {
        "name": PROJECT_NAME,
        "filter": 'metric.type="cloudfunctions.googleapis.com/function/user_memory_bytes"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }

    result = client.list_time_series(query)

    with open(CSV_MEMORY_USAGE_MB, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "function_name", "memory_usage_mb"])
        for data in result:
            for point in data.points:
                timestamp = point.interval.start_time
                value = point.value.distribution_value.mean
                writer.writerow(
                    [timestamp, data.resource.labels["function_name"], value]
                )


def startup_latencies():
    query = {
        "name": PROJECT_NAME,
        "filter": 'metric.type="run.googleapis.com/container/startup_latencies"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }

    result = client.list_time_series(query)

    with open(CSV_STARTUP_LATENCY_MS, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "service_name", "startup_latency_ms"])
        for data in result:
            for point in data.points:
                timestamp = point.interval.start_time
                value = point.value.distribution_value.mean
                writer.writerow(
                    [timestamp, data.resource.labels["service_name"], value]
                )


def execution_times():
    query = {
        "name": PROJECT_NAME,
        "filter": 'metric.type="cloudfunctions.googleapis.com/function/execution_times"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }

    result = client.list_time_series(query)

    with open(CSV_EXECUTION_TIME_MS, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "function_name", "execution_time_ms"])
        for data in result:
            for point in data.points:
                timestamp = point.interval.start_time
                value = point.value.distribution_value.mean
                writer.writerow(
                    [timestamp, data.resource.labels["function_name"], value]
                )


def cpu_usages():
    query = {
        "name": PROJECT_NAME,
        "filter": 'metric.type="run.googleapis.com/container/cpu/utilizations"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    }

    result = client.list_time_series(query)

    with open(CSV_CPU_USAGE_PERCENT, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "service_name", "cpu_usage_percent"])
        for data in result:
            for point in data.points:
                timestamp = point.interval.start_time
                value = point.value.distribution_value.mean
                writer.writerow(
                    [timestamp, data.resource.labels["service_name"], value]
                )


def fetch_data():
    active_instances()
    memory_usages()
    startup_latencies()
    execution_times()
    cpu_usages()
    pass


if __name__ == "__main__":
    fetch_data()

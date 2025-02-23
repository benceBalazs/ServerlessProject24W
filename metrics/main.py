import csv
import os
import subprocess
import time

from datetime import datetime, timedelta, UTC
from google.cloud import monitoring_v3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ID = "serverless-project-24w"
PROJECT_NAME = "projects/" + PROJECT_ID
FUNCTION_NAMES = [
    "input-handler",
    "metadata-extractor",
    "exif-processor",
    "format-converter",
    "rgb-channel-separator",
    "thumbnail-generator",
]

OUTPUTDIR = os.getenv("RESULTDIR", "./")

COLLECTION_WINDOW_MINUTES = int(float(os.getenv("COLLECTION_WINDOW_MINUTES", 10)))
COLLECTION_SLACK_MINUTES = 2

METRICS = {
    "execution_times": {
        "metric_type": "cloudfunctions.googleapis.com/function/execution_times",
        "value_type": "distribution_value.mean",
        "value_name": "execution_time",
    },
    "memory_usage": {
        "metric_type": "cloudfunctions.googleapis.com/function/user_memory_bytes",
        "value_type": "distribution_value.mean",
        "value_name": "memory_bytes",
    },
    "active_instances": {
        "metric_type": "cloudfunctions.googleapis.com/function/active_instances",
        "value_type": "int64_value",
        "value_name": "instance_count",
    },
    "execution_count": {
        "metric_type": "cloudfunctions.googleapis.com/function/execution_count",
        "value_type": "int64_value",
        "value_name": "count",
    },
}


def get_metric_value(point, value_type):
    """Extract metric value based on value type"""
    if "." in value_type:
        attr, subattr = value_type.split(".")
        return getattr(getattr(point.value, attr), subattr)
    return getattr(point.value, value_type)


def collect_metric(client, metric_config, start_time, end_time):
    metric_data = []
    interval = monitoring_v3.TimeInterval(
        {"start_time": start_time, "end_time": end_time}
    )

    for function_name in FUNCTION_NAMES:
        results = client.list_time_series(
            request={
                "name": PROJECT_NAME,
                "filter": f'metric.type="{metric_config["metric_type"]}" AND resource.labels.function_name="{function_name}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        for result in results:
            for point in result.points:
                metric_data.append(
                    {
                        "timestamp": point.interval.start_time.isoformat(),
                        "function": function_name,
                        metric_config["value_name"]: get_metric_value(
                            point, metric_config["value_type"]
                        ),
                    }
                )

    return metric_data


def save_metrics_to_csv(metrics_data):
    for metric_name, data in metrics_data.items():
        pd.DataFrame(data).to_csv(f"{OUTPUTDIR}{metric_name}.csv", index=False)


def plot_execution_times(df):
    if df.empty:
        print("No execution time data available")
        return

    plt.figure(figsize=(10, 6))

    # Calculate appropriate number of bins based on data size
    for function_name in df["function"].unique():
        function_data = df[df["function"] == function_name]
        n_points = len(function_data)
        # Use Sturges' rule or minimum of 5 bins
        n_bins = min(30, max(5, int(1 + 3.322 * np.log10(n_points))))

        plt.hist(
            function_data["execution_time"],
            bins=n_bins,
            alpha=0.5,
            label=function_name,
        )

    plt.title("Distribution of Execution Times")
    plt.xlabel("Execution Time (nanoseconds)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTDIR + "execution_times.png")
    plt.close()


def plot_memory_usage(df):
    if df.empty:
        print("No memory usage data available")
        return

    plt.figure(figsize=(10, 6))

    # Calculate appropriate number of bins based on data size
    for function_name in df["function"].unique():
        function_data = df[df["function"] == function_name]
        n_points = len(function_data)
        # Use Sturges' rule or minimum of 5 bins
        n_bins = min(30, max(5, int(1 + 3.322 * np.log10(n_points))))

        plt.hist(
            function_data["memory_bytes"],
            bins=n_bins,
            alpha=0.5,
            label=function_name,
        )

    plt.title("Memory Usage Distribution")
    plt.xlabel("Memory Usage (bytes)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTDIR + "memory_usage.png")
    plt.close()


def plot_active_instances(df):
    if df.empty:
        print("No active instances data available")
        return

    plt.figure(figsize=(10, 6))
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    for function_name in df["function"].unique():
        function_data = df[df["function"] == function_name]
        plt.plot(
            function_data["timestamp"],
            function_data["instance_count"],
            label=function_name,
            marker="o",
            linestyle="-",
            markersize=8,
        )

    # Format x-axis to show minutes
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # Set y-axis to use integer ticks
    ax = plt.gca()
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))

    plt.title("Active Instances")
    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Number of Active Instances")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTDIR + "active_instances.png")
    plt.close()


def plot_execution_count(df):
    if df.empty:
        print("No execution count data available")
        return

    plt.figure(figsize=(10, 6))
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    for function_name in df["function"].unique():
        function_data = df[df["function"] == function_name]
        plt.plot(
            function_data["timestamp"],
            function_data["count"],
            label=function_name,
            marker="o",
            linestyle="-",
            markersize=8,
        )

    # Format x-axis to show minutes
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # Set y-axis to use integer ticks
    ax = plt.gca()
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))

    plt.title("Function Executions")
    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Number of Executions")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTDIR + "execution_count.png")
    plt.close()


def create_plots(metrics_data):
    plotting_functions = {
        "execution_times": plot_execution_times,
        "memory_usage": plot_memory_usage,
        "active_instances": plot_active_instances,
        "execution_count": plot_execution_count,
    }

    print("\nCreating plots:")
    for metric_name, plot_func in plotting_functions.items():
        data = metrics_data.get(metric_name, [])
        if not data:
            print(f"Skipping {metric_name} plot - no data available")
            continue

        df = pd.DataFrame(data)
        if df.empty:
            print(f"Skipping {metric_name} plot - empty dataframe")
            continue

        print(f"Creating plot for {metric_name}")
        plot_func(df)


def main():
    client = monitoring_v3.MetricServiceClient()

    start_time = (
        datetime.now(UTC)
        - timedelta(minutes=COLLECTION_WINDOW_MINUTES)
        - timedelta(minutes=COLLECTION_SLACK_MINUTES)
    )
    end_time = datetime.now(UTC)

    metrics_data = {
        metric_name: collect_metric(client, config, start_time, end_time)
        for metric_name, config in METRICS.items()
    }

    print("\nCollected metrics summary:")
    for metric_name, data in metrics_data.items():
        print(f"{metric_name}: {len(data)} data points")

    save_metrics_to_csv(metrics_data)

    create_plots(metrics_data)


if __name__ == "__main__":
    main()

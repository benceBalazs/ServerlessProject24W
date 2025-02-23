import pandas as pd
import matplotlib.pyplot as plt
from defs import *


def plot_active_instances():
    df = pd.read_csv(CSV_ACTIVE_INSTANCES)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    df = df.sort_values("timestamp")

    plt.figure(figsize=(12, 6))

    # Plot each function with a different color
    for function_name in df["function_name"].unique():
        data = df[df["function_name"] == function_name]
        plt.plot(data["time"], data["active_instances"], label=function_name)

    plt.title("Active Instances Over Time by Function")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.ylabel("Number of Active Instances")

    plt.xlabel("Time (HH:mm)")
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(PLOT_ACTIVE_INSTANCES, dpi=900, bbox_inches="tight")
    plt.close()


def plot_cpu_usage():
    df = pd.read_csv(CSV_CPU_USAGE_PERCENT)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    df = df.sort_values("timestamp")

    plt.figure(figsize=(12, 6))

    # Plot each service with a different color
    for service_name in df["service_name"].unique():
        data = df[df["service_name"] == service_name]
        plt.plot(data["time"], data["cpu_usage_percent"], label=service_name)

    plt.title("CPU Usage Over Time by Service")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.ylabel("CPU Usage (%)")
    plt.xlabel("Time (HH:mm)")
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(PLOT_CPU_USAGE_PERCENT, dpi=900, bbox_inches="tight")
    plt.close()


def plot_execution_time():
    df = pd.read_csv(CSV_EXECUTION_TIME_MS)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    df = df.sort_values("timestamp")

    plt.figure(figsize=(12, 6))

    # Plot each function with a different color
    for function_name in df["function_name"].unique():
        data = df[df["function_name"] == function_name]
        plt.plot(data["time"], data["execution_time_ms"], label=function_name)

    plt.title("Execution Time Over Time by Function")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.ylabel("Execution Time (ms)")
    plt.xlabel("Time (HH:mm)")
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(PLOT_EXECUTION_TIME_MS, dpi=900, bbox_inches="tight")
    plt.close()


def plot_memory_usage():
    df = pd.read_csv(CSV_MEMORY_USAGE_MB)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    df = df.sort_values("timestamp")

    plt.figure(figsize=(12, 6))

    # Plot each function with a different color
    for function_name in df["function_name"].unique():
        data = df[df["function_name"] == function_name]
        plt.plot(data["time"], data["memory_usage_mb"], label=function_name)

    plt.title("Memory Usage Over Time by Function")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.ylabel("Memory Usage (MB)")
    plt.xlabel("Time (HH:mm)")
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(PLOT_MEMORY_USAGE_MB, dpi=900, bbox_inches="tight")
    plt.close()


def plot_startup_latency():
    df = pd.read_csv(CSV_STARTUP_LATENCY_MS)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    df = df.sort_values("timestamp")

    plt.figure(figsize=(12, 6))

    # Plot each service with a different color
    for service_name in df["service_name"].unique():
        data = df[df["service_name"] == service_name]
        plt.plot(data["time"], data["startup_latency_ms"], label=service_name)

    plt.title("Startup Latency Over Time by Service")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.ylabel("Startup Latency (ms)")
    plt.xlabel("Time (HH:mm)")
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(PLOT_STARTUP_LATENCY_MS, dpi=900, bbox_inches="tight")
    plt.close()


def create_plots():
    plot_active_instances()
    plot_cpu_usage()
    plot_execution_time()
    plot_memory_usage()
    plot_startup_latency()


if __name__ == "__main__":
    create_plots()

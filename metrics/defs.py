import os

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

CSV_ACTIVE_INSTANCES = OUTPUTDIR + "active_instances.csv"
CSV_MEMORY_USAGE_MB = OUTPUTDIR + "memory_usage_mb.csv"
CSV_CPU_USAGE_PERCENT = OUTPUTDIR + "cpu_usage.csv"
CSV_EXECUTION_TIME_MS = OUTPUTDIR + "execution_time.csv"
CSV_STARTUP_LATENCY_MS = OUTPUTDIR + "startup_latency.csv"

PLOT_ACTIVE_INSTANCES = OUTPUTDIR + "active_instances_plot.png"
PLOT_CPU_USAGE_PERCENT = OUTPUTDIR + "cpu_usage_plot.png"
PLOT_EXECUTION_TIME_MS = OUTPUTDIR + "execution_time_plot.png"
PLOT_MEMORY_USAGE_MB = OUTPUTDIR + "memory_usage_plot.png"
PLOT_STARTUP_LATENCY_MS = OUTPUTDIR + "startup_latency_plot.png"

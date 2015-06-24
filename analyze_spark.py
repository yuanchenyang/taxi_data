import argparse

from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext("local", "Taxi Data")
sqlContext = SQLContext(sc)

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Filename for input trip data")
args = parser.parse_args()

df = sqlContext.read.format('com.databricks.spark.csv').options(header='true').load(args.input_file)

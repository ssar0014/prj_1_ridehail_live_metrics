import os

if __name__ == "__main__":
    print(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "jars/flink-sql-connector-kafka-3.4.0-1.20.jar",
        )
    )

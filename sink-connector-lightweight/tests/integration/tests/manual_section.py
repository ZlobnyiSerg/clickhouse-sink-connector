from integration.tests.steps.sql import *
from integration.tests.steps.statements import *
from integration.tests.steps.service_settings_steps import *


@TestOutline
def mysql_to_clickhouse_connection(
    self,
    mysql_columns,
    clickhouse_table_engine,
    clickhouse_columns=None,
):
    """Basic check MySQL to Clickhouse connection by small and simple data insert."""

    table_name = f"manual_{getuid()}"

    mysql = self.context.cluster.node("mysql-master")

    with Given(f"I create MySql to CH replicated table", description=table_name):
        create_mysql_to_clickhouse_replicated_table(
            name=table_name,
            mysql_columns=mysql_columns,
            clickhouse_columns=clickhouse_columns,
            clickhouse_table_engine=clickhouse_table_engine,
        )

    with When(f"I insert data in MySql table"):
        complex_insert(
            node=mysql,
            table_name=table_name,
            values=["({x},{y})", "({x},{y})"],
            partitions=1,
            parts_per_partition=1,
            block_size=10,
        )

    with Then(
        "I check that MySQL tables and Clickhouse replication tables have the same data"
    ):
        complex_check_creation_and_select(
            table_name=table_name,
            clickhouse_table_engine=clickhouse_table_engine,
            statement="count(*)",
            with_final=True,
        )


@TestFeature
@Name("mysql to clickhouse")
def mysql_to_clickhouse(
    self,
    mysql_columns="MyData INT",
    clickhouse_columns="MyData Int32",
):
    """Just imitation of tests."""
    for clickhouse_table_engine in self.context.clickhouse_table_engines:
        if self.context.env.endswith("auto"):
            with Example({clickhouse_table_engine}, flags=TE):
                mysql_to_clickhouse_connection(
                    mysql_columns=mysql_columns,
                    clickhouse_columns=clickhouse_columns,
                    clickhouse_table_engine=clickhouse_table_engine,
                )


@TestModule
@Name("manual section")
def module(self):
    """MySql to ClickHouse replication manual checks section."""

    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()
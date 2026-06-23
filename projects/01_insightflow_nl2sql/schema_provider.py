"""将现有 Schema Catalog 转换为 Pydantic Snapshot。"""

from contracts import ColumnSchema, SchemaSnapshot, TableSchema
from schema_catalog import SCHEMA_CATALOG


def build_schema_snapshot() -> SchemaSnapshot:
    """返回 SQL 生成与校验共用的确定性 Schema 快照。"""
    return SchemaSnapshot(
        tables=[
            TableSchema(
                name=table_name,
                columns=[
                    ColumnSchema(
                        name=column_name,
                        semantic_type=column_definition["semantic_type"],
                    )
                    for column_name, column_definition in table_definition[
                        "columns"
                    ].items()
                ],
            )
            for table_name, table_definition in SCHEMA_CATALOG.items()
        ]
    )

import duckdb
import pandas as pd
from loguru import logger

logger.info("Connecting to DB...")
conn = duckdb.connect("/home/mohammadi/bioregistry.db")

logger.info("Reading PyArrow Parquet...")
df = pd.read_parquet(
    "/home/mohammadi/datasets/network/public/kg/open_targets/25.03/association_overall_direct/*.parquet",
    engine="pyarrow",
)

logger.info(f"Loaded {len(df)} associations. Preview:")
print(df.head())

logger.info("Executing JOIN test...")
res = conn.execute(
    "SELECT COUNT(*) FROM df JOIN v_translate_id v ON df.targetId = v.input_id AND v.canonical_type = 'Gene'"
).df()

logger.success("Done!")
print(res)

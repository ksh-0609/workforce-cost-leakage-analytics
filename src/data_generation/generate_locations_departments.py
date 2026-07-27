from db_connection import get_engine
import pandas as pd

locations = pd.DataFrame({
    "name": [
        "Northgate",
        "Riverside",
        "Maple Street",
        "Harbor View",
        "Lakeside"
    ],
    "city": [
        "Fairview",
        "Fairview",
        "Brookhaven",
        "Brookhaven",
        "Elmwood"
    ]
})

departments = pd.DataFrame({
    "name": [
        "Sales Floor",
        "Stockroom",
        "Customer Service",
        "Cash Counter",
        "Management"
    ]
})

engine = get_engine()

locations.to_sql(
    "locations",
    con=engine,
    if_exists="append",
    index=False
)

departments.to_sql(
    "departments",
    con=engine,
    if_exists="append",
    index=False
)

print(f"Inserted {len(locations)} locations and {len(departments)} departments.")
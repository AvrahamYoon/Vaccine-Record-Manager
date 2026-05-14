-- One bound parameter (?): absolute path to vaccine_records_cleaned.csv
-- all_varchar=true matches prior pandas read_csv(..., dtype=str).
SELECT *
FROM read_csv_auto(
    ?,
    header = true,
    all_varchar = true
);

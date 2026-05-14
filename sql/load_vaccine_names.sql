-- One bound parameter (?): absolute path to vaccine_names.csv
SELECT *
FROM read_csv_auto(
    ?,
    header = true,
    all_varchar = true
);

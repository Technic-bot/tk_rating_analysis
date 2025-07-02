# Preprocessing to get csv
python3 utils/clean_data.py data/sketch-2022-10-25.json data/sketch-2022-10-25.csv
# Grouping each 1 months
python3 get_lewd_ratio.py ../data/color-3-dic-21.csv --time 2018-01-01 --freq 1 --prefix graphs/nox-

# new sintax
python rating_analysis/get_lewd_ratio.py data/tom-2023-09-1-color.csv  --time-start 2015-09-01 --time-stop 2023-09-01 --freq 3 --prefix rating_analysis/graphs/2023/tom-2023-09-01-color

python rating_analysis/get_lewd_ratio.py data/2024/tom-2024-01-30.csv --time-start 2015-09-01 --time-stop 2023-09-01 --freq 3 --prefix rating_analysis/graphs/2024/tom-2024-01-30

python rating_analysis/get_lewd_ratio.py data/2025/tom-30-jun-25.csv --time-start 2015-09-01 --freq 3 --title "All Art" --prefix rating_analysis/graphs/2025/tom-2025-06-30

python rating_analysis/get_lewd_ratio.py data/2025/tom-color-30-jun-25.csv --time-start 2015-09-01 --freq 3 --title "Colored Art" --prefix rating_analysis/graphs/2025/tom-color-2025-06-30








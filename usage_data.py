import pyarrow.parquet as pq
import pandas as pd
import json
from config import create_parser, Config
parser = create_parser()
args, _ = parser.parse_known_args()
config = Config(args)


# Read dataset
dataset = pq.ParquetDataset(config.data_path / "revlogs")
table = dataset.read()
df = table.to_pandas()

# Ensure day_offset is int
df['day_offset'] = df['day_offset'].astype(int)

# Filter new cards
df_new = df[df['state'] == 0]

# Per-user stats
user_stats = {}

for user_id in df['user_id'].unique():
    user_df = df[df['user_id'] == user_id]
    days_active = user_df['day_offset'].nunique()

    if days_active == 0:
        continue

    total_duration = user_df['duration'].sum()  # Total time in ms
    total_reviews = len(user_df)
    
    # New cards
    new_cards_count = len(df_new[df_new['user_id'] == user_id])

    # Compute averages per day
    avg_duration_per_day = float(f"{total_duration / days_active:.2f}")
    avg_reviews_per_day = total_reviews / days_active
    avg_new_cards_per_day = new_cards_count / days_active

    user_stats[user_id] = {
        'avg_duration_per_day': avg_duration_per_day,
        'avg_reviews_per_day': float(f"{avg_reviews_per_day:.2f}"),
        'avg_new_cards_per_day': float(f"{avg_new_cards_per_day:.2f}"),
        'active_days': days_active
    }

# Save to JSON
result_file = Path(f"result/usage_data.jsonl")
with open(result_file, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(user_stats, ensure_ascii=False) + "\n")

print(f"Saved average daily stats per user to {output_path}")
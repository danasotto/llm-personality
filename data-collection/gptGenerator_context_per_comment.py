import os
import openai
from openai import OpenAI
import pandas as pd

# Set your OpenAI API key here
openai.api_key = '<add your key>'

df = pd.read_csv("unique_posts_with_long_comment_counts.csv")

# GPT settings
temperature = 0
model = "gpt-4.1"
output_file = "gpt4.1_generated_comments.csv"

# Initialize output DataFrame (load existing if continuing)
if os.path.exists(output_file):
    output_df = pd.read_csv(output_file)
    processed_post_ids = set(output_df['post_id'])
    print(f"Resuming... already processed {len(processed_post_ids)} posts.")
else:
    output_df = pd.DataFrame()
    processed_post_ids = set()

# Prepare output rows list for temporary batch save
output_rows = []

# Loop through a shuffled sample of posts
for index, row in df.sample(frac=1, random_state=42).iterrows():
    post_id = row['post_id']
    if post_id in processed_post_ids:
        continue  # Skip already-processed posts

    title = row['post_title']
    text = row['post_text']
    num_long_comments = int(row['num_long_comments'])

    prompt = (
        "You are a Reddit user. "
        "Generate a comment to this Reddit post:\n\n"
        f"Post's title: {title}\n"
        f"Post content: {text}\n\n"
        "Return only the comment with no further content."
    )

    for i in range(num_long_comments):
        try:
            response = openai.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt,
                }]
            )

            comment = response.choices[0].message.content

            # Build output row
            output_row = row.to_dict()
            output_row['generated_comment'] = comment
            output_rows.append(output_row)

        except Exception as e:
            print(f"Error generating comment {i+1} for post {post_id}: {e}")

    # Save after each post
    if output_rows:
        new_df = pd.DataFrame(output_rows)
        new_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
        print(f"wrote to file post: {post_id}")
        output_rows = []  # clear for next post

print("Finished.")


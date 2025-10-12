import os
import openai
from openai import OpenAI
import pandas as pd
import re


# Set your OpenAI API key here
openai.api_key = '<add your key>'

df = pd.read_csv("unique_posts_with_long_comment_counts.csv")

# GPT settings
temperature = 0.7
model = "gpt-4.1-mini"
#gpt-4-1-mini
output_file = "GPT4.1-Mini_temp_0.7_generated_comments.csv"

current_df_len = 0

# Initialize output DataFrame (load existing if continuing)
if os.path.exists(output_file):
    output_df = pd.read_csv(output_file)
    initial_df_len = len(output_df)
    current_df_len = initial_df_len
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

    # prompt = (
    #     "You are a Reddit user. "
    #     "Generate a comment to this Reddit post:\n\n"
    #     f"Post's title: {title}\n"
    #     f"Post content: {text}\n\n"
    #     "Return only the comment with no further content."
    # )
    
    # prompt = (
    #     "You are a Reddit user. "
    #     f"Generate {num_long_comments} comments "
    #     f"in response to the following Reddit post. Number each comment:\n\n"
    #     f"Post's title: {title}\n"
    #     f"Post content: {text}\n\n"
    #     "Only return the numbered list of comments."
    # )

    prompt = (
        "You are several Reddit users. "
        f"Generate {num_long_comments} comments, at least 100 words long,  "
        f"in response to the following Reddit post. Number each comment:\n\n"
        f"Post's title: {title}\n"
        f"Post content: {text}\n\n"
        "Only return the numbered list of comments."
    )

    min_num_of_tokens = 100*num_long_comments+10 #at least 100 tokens per comment
    try:
        response = openai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": prompt,
            }]
        )


        all_comments = response.choices[0].message.content

        # Split by line or numbered list
        comment_lines = [line.strip() for line in all_comments.split("\n") if line.strip()]
        numbered_comments = []
        current_comment = ""

        pattern = re.compile(r'^(\d+)[.)]?\s*(.*)') 

        for line in comment_lines:
            line = line.strip()
            match = pattern.match(line)

            if match:
                # New numbered item
                if current_comment:
                    numbered_comments.append(current_comment.strip())

                text = match.group(2)

                if text:
                    # Comment starts on same line
                    current_comment = text
                    expecting_new_comment = False
                else:
                    # Comment will start on the next line
                    current_comment = ""
                    expecting_new_comment = True
            else:
                # If we were expecting a new comment, start it here
                if expecting_new_comment:
                    current_comment = line
                    expecting_new_comment = False
                else:
                    # Continue the current comment
                    current_comment += " " + line

        # Add the last comment
        if current_comment:
            numbered_comments.append(current_comment.strip())

        # Save each comment as separate row
        for comment in numbered_comments:
            output_row = row.to_dict()
            output_row['generated_comment'] = comment
            output_rows.append(output_row)

    except Exception as e:
        print(f"Error generating comments for post {post_id}: {e}")

    # Save after each post
    if output_rows:
        current_df_len = current_df_len + len(output_rows)
        new_df = pd.DataFrame(output_rows)
        new_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
        print(f"Wrote {len(numbered_comments)} comments for post {post_id}")
        if len(numbered_comments) != num_long_comments:
            print (all_comments)
        output_rows = []  # clear for next post
        if (current_df_len > 10000):
            exit()

print("Finished.")


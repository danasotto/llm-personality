# comments file manipulations

import pandas as pd

def remove_quoted_lines(text):
    lines = str(text).split('\n')
    non_quoted_lines = [line for line in lines if not line.strip().startswith('>')]
    return '\n'.join(non_quoted_lines).strip()

def compare_posts_within_comments_files():
   
    # Load the two CSV files
    df1 = pd.read_csv("data-scores\llm models with predictions\generated_comments_Qwen2.5-72B-instruct_temp-0.7_with_predictions.csv")
    df2 = pd.read_csv("data-scores\llm models with predictions\generated_comments_granite-3.3-8b-instruct_temp-0.0_with_predictions.csv")

    # Get the sets of post_ids (since post_id is not unique)
    set1 = set(df1['post_id'])
    set2 = set(df2['post_id'])

    # Calculate intersection
    shared_ids = set1.intersection(set2)

    # Percent overlap
    percent_overlap_1 = len(shared_ids) / len(set1) * 100  # % of file1 IDs in file2
    percent_overlap_2 = len(shared_ids) / len(set2) * 100  # % of file2 IDs in file1

    print(f"Shared post_ids: {len(shared_ids)}")
    print(f"Total in file1: {len(set1)}, overlap: {percent_overlap_1:.2f}%")
    print(f"Total in file2: {len(set2)}, overlap: {percent_overlap_2:.2f}%")

compare_posts_within_comments_files()
exit()
# # Load your CSV
# df = pd.read_csv('data-scores/comments_with_predictions_over_100_words.csv')

# # Clean each comment by removing lines that start with '>'
# df['comment_text'] = df['comment_text'].apply(remove_quoted_lines)

# # Save the cleaned version
# df.to_csv('comments_with_predictions_over_100_words_no_quotes.csv', index=False)
# print("Done: quoted lines removed.")


# Load your CSV
df = pd.read_csv('data-scores/comments_with_predictions_over_100_words_no_quotes.csv')
df['comment_word_count'] = df['comment_text'].str.split().str.len()
# Save the cleaned version
df.to_csv('data-scores/comments_with_predictions_over_100_words_no_quotes_temporary.csv', index=False)
df = pd.read_csv('data-scores/comments_with_predictions_over_100_words_no_quotes_temporary.csv')
filtered_df = df[df['comment_word_count'] >= 100]

# Save the filtered data to a new Excel file
filtered_df.to_csv('data-scores/comments_with_predictions_over_100_words_no_quotes_new.csv', index=False)

print("done")



# # Read CSV file into a DataFrame
# df = pd.read_csv('data-scores/reddit_comments_with_predictions.csv')
    

# # Read the CSV file
# df = pd.read_csv("data-scores/comments_with_predictions_over_100_words.csv")  

# # Drop duplicate posts based on 'post_id'
# # Keep only the first occurrence of each unique post
# unique_posts = df.drop_duplicates(subset='post_id')

# # Optionally, keep only post-related columns
# post_columns = ['post_id', 'post_subreddit', 'post_title', 'post_text',
#                 'post_flair', 'post_score', 'post_url', 'post_created_utc', 'post_num_comments']
# unique_posts = unique_posts[post_columns]

# # Save to a new CSV
# unique_posts.to_csv("unique_posts.csv", index=False)
# df = pd.read_csv('reddit_posts_clean.csv')


# # Read the original CSV file
# df = pd.read_csv("data-scores/comments_with_predictions_over_100_words.csv")  

# # Ensure 'comment_word_count' is numeric
# df['comment_word_count'] = pd.to_numeric(df['comment_word_count'], errors='coerce')

# # Count how many comments per post have >= 100 words
# long_comments_count = (
#     df
#     .groupby('post_id')
#     .size()
#     .reset_index(name='num_long_comments')
# )


# # Drop duplicate posts to get unique posts
# unique_posts = df.drop_duplicates(subset='post_id')

# # Keep only post-related columns
# post_columns = ['post_id', 'post_subreddit', 'post_title', 'post_text',
#                 'post_flair', 'post_score', 'post_url', 'post_created_utc', 'post_num_comments']
# unique_posts = unique_posts[post_columns]

# # Merge the long comment count with the unique posts
# unique_posts = unique_posts.merge(long_comments_count, on='post_id', how='left')

# # Fill posts that had 0 long comments with 0
# unique_posts['num_long_comments'] = unique_posts['num_long_comments'].fillna(0).astype(int)

# # Save to a new CSV
# unique_posts.to_csv("unique_posts_with_long_comment_counts.csv", index=False)
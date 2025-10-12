import time
import pandas as pd

#  remove duplicated rows from dataframe according to the post_id and comment_id
def remove_duplicates(df):
    df.drop_duplicates(subset=['post_id', 'comment_id'], inplace=True)
    return df

# write a main code to read data from csv file and remove duplicates
def main():
    posts_comments_df = pd.read_csv('reddit_posts.csv')
    posts_comments_df = remove_duplicates(posts_comments_df)
    posts_comments_df.to_csv('reddit_posts_dedup.csv', index=False)

# run main code
if __name__ == "__main__":
    main()
import time
import pandas as pd
import praw

subreddits = [
    # Technology
    "technology", "programming", "webdev", "coding", "learnprogramming", 
    "compsci", "javascript", "python", "machinelearning", "datascience",
    "androiddev", "iOSProgramming", "cybersecurity", "hacking", "privacy",

    # Science
    "science", "askscience", "physics", "chemistry", "biology", 
    "astronomy", "space", "medicine", "neuroscience", "ecology",
    "geology", "math", "statistics", "engineering", "materials",

    # Entertainment
    "movies", "television", "music", "books", "gaming",
    "anime", "manga", "comics", "netflix", "youtube",
    "twitch", "podcasts", "boardgames", "scifi", "fantasy",

    # Lifestyle
    "fitness", "nutrition", "cooking", "food", "recipes",
    "fashion", "malefashionadvice", "femalefashionadvice", "makeup",
    "travel", "backpacking", "camping", "hiking", "photography",

    # Social
    "askreddit", "casualconversation", "relationship_advice", "dating_advice", "socialskills",
    "advice", "nostupidquestions", "tooafraidtoask", "explainlikeimfive", "outoftheloop",
    "changemyview", "unpopularopinion", "amitheasshole", "tifu", "confession",

    # Finance
    "personalfinance", "investing", "financialindependence", "frugal",
    "stocks", "cryptocurrency", "bitcoin", "ethereum", "wallstreetbets",
    "realestate", "credit", "tax", "studentloans", "povertyfinance",

    # Career
    "jobs", "careerguidance", "resumes", "interviews", "cscareerquestions",
    "engineeringstudents", "gradschool", "professors", "teachers", "lawschool",
    "medicalschool", "nursing", "dentistry", "pharmacy", "veterinary",

    # Health
    "health", "mentalhealth", "anxiety", "depression", "adhd",
    "autism", "bipolar", "ptsd", "ocd", "eatingdisorders",
    "weightloss", "loseit", "gainit", "sleep", "meditation",

    # Hobbies
    "gardening", "houseplants", "diy", "crafts", "woodworking",
    "knitting", "crochet", "sewing", "painting", "drawing",
    "writing", "poetry", "journaling", "calligraphy", "lettering",

    # Sports
    "sports", "nfl", "nba", "soccer", "baseball",
    "hockey", "tennis", "golf", "running", "swimming",
    "cycling", "climbing", "skiing", "snowboarding", "martialarts",

    # Parenting
    "parenting", "mommit", "daddit", "newparents", "beyondthebump",
    "toddlers", "teenagers", "adoption", "fosterparents", "stepparents",
    "breastfeeding", "babybumps", "tryingforababy", "infertility", "namenerds",

    # Pets
    "pets", "dogs", "cats", "aquariums", "reptiles",
    "birds", "rabbits", "hamsters", "guineapigs", "ferrets",
    "dogtraining", "puppy101", "catadvice", "vettech", "askvet",

    # Home
    "homeimprovement", "homeowners", "interiordesign", "homedecorating", "organization",
    "declutter", "konmari", "minimalism", "cleaning", "homeautomation",
    "smarthome", "homenetworking", "homesecurity", "lawncare", "landscaping",

    # Education
    "education", "teachers", "homeschool", "college", "applyingtocollege",
    "gradschool", "studentloans", "study", "homework", "testprep",
    "sat", "act", "gre", "mcat", "lsat",

    # Location-based
    "nyc", "losangeles", "chicago", "seattle", "boston",
    "sanfrancisco", "portland", "austin", "denver", "atlanta",
    "london", "toronto", "sydney", "melbourne", "berlin",

    # Miscellaneous
    "history", "philosophy", "politics", "worldnews", "news",
    "futurology", "environment", "climate", "sustainability", "zerowaste",
    "minimalism", "anticonsumption", "buyitforlife", "thriftstorehauls", "simpleliving"
]


def get_comments(posts_df, minimum_comments, comments_limit, last_post_id):
    comments_list = []
    comments_collected = 0

    try:
        if last_post_id:
            start_index = posts_df[posts_df['id'] == last_post_id].index[0]
        else:
            start_index = 0

        # for index, row in posts_df.iterrows():
        for index, row in posts_df.iloc[start_index:].iterrows():
            # if (index + 1) % 1000 == 0:
            #     time.sleep(600)  # Sleep for 2 second

            if row['num_comments'] > 1500:
                print (f"Skipping post {row['id']} because it has {row['num_comments']} comments")
                continue
            
            # Access data in the row
            submission = reddit.submission(id=row['id'])
            submission.comments.replace_more(limit=None)  # Set limit=0 for only top-level comments
            for top_level_comment in submission.comments:
                if top_level_comment.body and (len(top_level_comment.body.strip()) > 0) and (len(top_level_comment.body.split()) >= 40) and top_level_comment.submission.num_comments < 1500:
                    comment_data = {
                        # 'top_level_comment'
                        'post_id':top_level_comment.submission.id,
                        'post_subreddit': top_level_comment.submission.subreddit.display_name,
                        'post_title': top_level_comment.submission.title,
                        'post_text': top_level_comment.submission.selftext,
                        'post_flair': top_level_comment.submission.link_flair_text,
                        'post_score': top_level_comment.submission.score,
                        'post_url': top_level_comment.submission.url,
                        'post_created_utc': top_level_comment.submission.created_utc,
                        'post_num_comments': top_level_comment.submission.num_comments,
                        'comment_id': top_level_comment.id,
                        'comment_text': top_level_comment.body
                    }
                
                    comments_list.append(comment_data)
                    comments_collected += 1
                    if comments_collected % 100 == 0:
                        print (f"Collected {comments_collected} comments")

                if comments_collected >= comments_limit:
                    comments_collected = 0
                    break
    except Exception as e:
        print(f"Got this error: {e}")

    return (comments_list)

def get_posts(subreddit_name, post_limit, limit=1000):
    subreddit = reddit.subreddit(subreddit_name)
    collected_posts = []
    seen_post_ids = set()

    # Define the flairs we want to search for
    flairs = ["Question", "Ask", "Advise", "Discussion", "Poll"]
    search_query = " OR ".join([f"flair:{flair}" for flair in flairs])

    # For Reddit's search API, we need to handle pagination manually
    after = None
    batch_size = 100  # Reddit API typically allows up to 100 per request

    while len(collected_posts) < limit:
        try:
            # Get a batch of posts - PRAW handles the 'after' parameter differently
            if after:
                search_results = list(subreddit.search(
                    search_query, 
                    sort="new", 
                    limit=batch_size,
                    params={'after': after}
                ))
            else:
                search_results = list(subreddit.search(
                    search_query, 
                    sort="new", 
                    limit=batch_size
                ))

            # If we got no results, we've reached the end
            if not search_results:
                print("No more posts to fetch")
                break

            # Process the batch
            for post in search_results:
                if post.id in seen_post_ids:
                    continue

                seen_post_ids.add(post.id)

                post_data = {
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'score': post.score,
                    'reddit_url': post.permalink,
                    'created_utc': post.created_utc,
                    'id': post.id,
                    'selftext': post.selftext,
                    'num_comments': post.num_comments,
                    'upvote_ratio': post.upvote_ratio,
                    'flair': post.link_flair_text if hasattr(post, 'link_flair_text') else None
                }
                collected_posts.append(post_data)

                if len(collected_posts) >= limit:
                    break

            # Get the fullname of the last post for pagination
            if search_results:
                after = f"t3_{search_results[-1].id}"
            else:
                after = None

            print(f"Collected {len(collected_posts)} posts so far")
            time.sleep(1)  # Respect API rate limits

        except Exception as e:
            print(f"Error fetching posts: {e}")
            print(f"Current after value: {after}")
            time.sleep(5)  # Wait longer on error
            return collected_posts

    return collected_posts

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id="<replace-client-id>",
    client_secret="<replace-client-secret>",
    user_agent="MyBot/0.0.1"
)

def save_reddit_posts():
    # Calculate posts needed per subreddit to reach approximately 50,000 posts
    #posts_per_subreddit = 2500  # 2500 * 20 subreddits = 50,000 posts
    posts_per_subreddit = 2000

    all_posts = []
    total_posts = 0
    for subreddit in subreddits:
        print(f"Fetching posts from r/{subreddit}")
        posts = get_posts(subreddit, posts_per_subreddit)
        all_posts.extend(posts)
        total_posts += len(posts)
        print(f"Collected {len(posts)} posts from r/{subreddit}")
        print(f"Total posts so far: {total_posts}")

        # Be nice to Reddit's API
        time.sleep(2)

    # Convert to DataFrame
    posts_df = pd.DataFrame(all_posts)

    # Remove any duplicate posts based on post ID
    posts_df = posts_df.drop_duplicates(subset='id')
    print(f"Total posts after dedup: {len(posts_df)}")

    # Trim to exactly 50,000 posts if we have more
    if len(posts_df) > 50000:
        posts_df = posts_df.sample(n=50000, random_state=42)

    posts_df.to_csv('posts.csv', index=False)

def save_post_and_comments(posts_df, last_post_id=None, existing_comments_df=None):
    comments = get_comments(posts_df,1, comments_limit=20, last_post_id=last_post_id)
    comments_df = pd.DataFrame(comments)

    if existing_comments_df is not None:
        comments_df = pd.concat([existing_comments_df, comments_df], ignore_index=True)

    # Save to CSV
    comments_df.to_csv('reddit_posts.csv', index=False)

    print(f"Final number of posts collected: {len(comments_df)}")
    print("Data saved to reddit_posts.csv")

if __name__ == "__main__":

    for i in range(30):
        try:
            posts_df = pd.read_csv("posts.csv")
            print("Saving posts and comments...")
            try:
                tmp_posts_comments_df = pd.read_csv("reddit_posts.csv")
                # get the last post id from the tmp_posts_comments_df
                if len(tmp_posts_comments_df) > 0:
                    last_post_id = tmp_posts_comments_df['post_id'].iloc[-1]
                print(f"Will continue from post {last_post_id}")
            except:
                tmp_posts_comments_df = None
                last_post_id = None
                
            save_post_and_comments(posts_df, last_post_id, tmp_posts_comments_df)
        except:
            print("Error in saving posts and comments")
            time.sleep(60)

# TODO: show which character was used
# TODO: show leaderboard based on argument1 which is starting point

from warnings import filterwarnings
from upstash_redis import Redis
import scratchattach as sa
from dotenv import load_dotenv
import os

load_dotenv()

redis = Redis.from_env()

filterwarnings('ignore', category=sa.LoginDataWarning)

session = sa.login_by_id(str(os.getenv("SCRATCH_SESSION_ID")), username="SupKittyMeow")
cloud = session.connect_cloud("1175964459")
client = cloud.requests()

@client.event
def on_ready(): # just to make sure everything is working
    print("Request handler is running", flush=True)
    if redis.ping() == "PONG":
        print("Redis is running!", flush=True)

@client.request
def ping(): # sends back 'pong' to the Scratch project
    return "pong"

@client.request
def add_score(argument1): # sets the score of the user to the second argument, saved to a database
    try:
        score = int(argument1)
    except ValueError:
        return "Error: Score must be a whole number!"
    
    redis.zadd('leaderboard', {client.get_requester(): score} )
    return "score set"

@client.request
def get_score(argument1): # retrieve a user's score
    response = redis.zscore('leaderboard', argument1)

    # Check if the player exists in the leaderboard
    if response is not None:
        # If player exists, return the data
        try:
            return int(response)
        except ValueError:
            # This should never happen but who knows
            return 0
    else:
        # If player doesn't exist, return 0
        return 0
    
@client.request
def reset_score(): # deletes the user's score from the database
    redis.zrem('leaderboard', client.get_requester())
    return "RESET"

@client.request
def get_leaderboard(leaderboardStart): # returns a list of the top 5 scores
    try:
        leaderboardStart = int(leaderboardStart)
    except ValueError:
        return "Error: Leaderboard start must be a whole number!"

    descending_users = redis.zrange('leaderboard', leaderboardStart, leaderboardStart + 4, withscores=True, rev=True)
    
    leaderboard_list = [ f"{user[0]}: {int(user[1])}" for user in descending_users ]
    leaderboard_list.append(str(redis.zcard('leaderboard')))
    return leaderboard_list

client.start(thread=True)
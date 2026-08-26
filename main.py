# TODO: show which character was used

from warnings import filterwarnings
from upstash_redis import Redis
import scratchattach as sa
from dotenv import load_dotenv
import os

load_dotenv()

redis = Redis.from_env()

filterwarnings('ignore', category=sa.LoginDataWarning)

USERNAME = "SupKittyMeow"
PROJECT_ID = "1175964459"
CONTACT = "amazing-game-idk-nam.service715@passmail.net"

session = sa.login_by_id(str(os.getenv("SCRATCH_SESSION_ID")), username=USERNAME)
cloud = session.connect_cloud(PROJECT_ID)
client = cloud.requests()

tw_cloud = sa.get_tw_cloud(PROJECT_ID, purpose="A leaderboard system for my game!", contact=CONTACT, cloud_host="wss://clouddata.turbowarp.org")
tw_client = tw_cloud.requests()

@client.event
def on_ready(): # just to make sure everything is working
    print("Scratch request handler is running", flush=True)
    if redis.ping() == "PONG":
        print("Redis is running!", flush=True)

@tw_client.event
def on_ready(): # just to make sure everything is working
    print("TurboWarp request handler is running", flush=True)
    if redis.ping() == "PONG":
        print("Redis is running!", flush=True)


@client.request
def ping(): # sends back 'pong' to the Scratch project
    return "pong"

@tw_client.request
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

@tw_client.request
def add_score(argument1, argument2): # sets the score of the user to the second argument, saved to a database
    try:
        score = int(argument1)
    except ValueError:
        return "Error: Score must be a whole number!"
    
    redis.zadd('leaderboard_tw', {argument2: score} )
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
    
@tw_client.request
def get_score(argument1): # retrieve a user's score
    response = redis.zscore('leaderboard_tw', argument1)

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

@tw_client.request
def reset_score(argument1): # deletes the user's score from the database
    redis.zrem('leaderboard_tw', argument1)
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

@tw_client.request
def get_leaderboard(leaderboardStart): # returns a list of the top 5 scores
    try:
        leaderboardStart = int(leaderboardStart)
    except ValueError:
        return "Error: Leaderboard start must be a whole number!"

    descending_users = redis.zrange('leaderboard_tw', leaderboardStart, leaderboardStart + 4, withscores=True, rev=True)
    
    leaderboard_list = [ f"{user[0]}: {int(user[1])}" for user in descending_users ]
    leaderboard_list.append(str(redis.zcard('leaderboard_tw')))
    return leaderboard_list

client.start(thread=True)
tw_client.start(thread=True)
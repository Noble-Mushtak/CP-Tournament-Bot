# Competitive Programming Tournament Bot

This GitHub repository holds a Python bot which can be used to hold a Swiss-style competitive programming contest. Here's some instructions on how to use the bot: (note that in the instructions below, it is assumed that `python` is Python 3, you may need to run `python3` instead if `python` on your system is Python 2)

Step 1: Run the following commands:

    git clone <github-repo>
    cd <directory>
    pip install -r requirements.txt

Step 2: In the directory containing `bot.py`, create a `points.txt` where each line is of the form `<name> <atcoder_username> <codeforces_username> 0`. The 0 represents every person starts out with 0 points. If there are some helpers who are designated who are only planning on playing the people who get "byes" in certain rounds, then give them 1000 points instead of 0 so the helpers are in their own group.

Step 3: Run `python bot.py gen_pairs`, which will give you a list of pairings for people to play against each other. Note that only people with the same number of points will be paired against each other. If there is an odd number of people for some point group, one person will get a bye, and their points will automatically be incremented by 1. The pairings will be outputted to standard output and saved in `pairs.txt`, where each line in `pairs.txt` will have the form `<user1> <user2> beg`. The "beg" represents that this pairing will have beginner-level difficulty problems.

Step 4: Edit `pairs.txt` appropriately. For example, you can change "beg" to "med" to give this pairing medium-level difficulty problems. If someone received a bye and they want to play one of the helpers, you can edit `pairs.txt` to add a match between the person who got a bye and one of the helpers.

Step 5: Run `python bot.py gen_matches`, which will give each pairing a list of problems for their match. The links to the problems will be outputted to standard output and the problems for each pairing will also be saved in `matches.txt`.

Step 6: Share the problem information with all the competitors and set a timer for when the match should end.

Step 7: Once the match ends, run `python bot.py upd_matches`, which will decide who won each match and update the points in `points.txt` accordingly.

Step 8: If you would like to play another round of matches, go back to Step 3.

# Matches

In every match, a pairing is given 3 problems: The first problem is worth 100 points, the second problem is worth 200 points, and the third problem is worth 300 points. For beginner-level matches, the first problem is problem A from an AtCoder Beginner Contest, the second problem is problem B from an AtCoder Beginner Contest, and the third problem is an 800-rating problem from CodeForces. For medium-level matches, the first problem is an 800-rating problem from CodeForces, the second problem is a 1000-rating problem from CodeForces, and the third problem is a 1200-rating problem from CodeForces.

The person who gets the most points wins the match. If both people in the pairing get the same number of points, then the person who made their last submission first wins the match.
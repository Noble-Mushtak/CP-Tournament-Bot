import random
import sys
import aiohttp
import asyncio
import atcoder.submission
import json
import datetime

async def cfproblems(client_session):
    async with client_session.get("https://codeforces.com/api/problemset.problems") as resp:
        assert resp.status == 200
        return json.loads(await resp.text())["result"]["problems"]

async def earliest_ac(client_session, username, contest_id, task_id):
    earliest_datetime = None
    async for submission in atcoder.submission.fetch_all_submission_results(client_session, contest_id, atcoder.submission.SubmissionsSearchParams(username=username, task_id=task_id, status="AC")):
        cur_time = submission.summary.datetime.astimezone(tz=None)
        if earliest_datetime == None or earliest_datetime > cur_time:
            earliest_datetime = cur_time
    return earliest_datetime

async def earliest_cf(client_session, username, contest_id, task_id):
    earliest_datetime = None
    async with client_session.get(f"https://codeforces.com/api/user.status?handle={username}") as resp:
        assert resp.status == 200
        submissions = json.loads(await resp.text())["result"]
        for sub in submissions:
            try:
                cur_time = datetime.datetime.fromtimestamp(sub["creationTimeSeconds"]).astimezone(tz=None)
                if sub["verdict"] == "OK" and sub["contestId"] == contest_id and sub["problem"]["index"] == task_id and (earliest_datetime == None or earliest_datetime > cur_time):
                    earliest_datetime = cur_time
            except KeyError:
                pass
    return earliest_datetime

def read_points():
    pts_map = {}
    with open("points.txt", "r") as file:
        for line in file:
            if line == "":
                continue
            toks = line.split()
            pts_map[toks[0]] = (toks[1], toks[2], int(toks[3]))
    return pts_map

def write_points(pts_map):
    with open("points.txt", "w") as file:
        for username, info in pts_map.items():
            print(username, info[0], info[1], info[2], file=file)

def select_cf_prob(rating_group):
    while True:
        try:
            prob = random.choice(rating_group)
            contestId = prob["contestId"]
            index = prob["index"]
            return f"{contestId}-{index}", f"https://codeforces.com/contest/{contestId}/problem/{index}"
        except KeyError:
            pass
            
def gen_beg_match(rating_groups):
    first_ac = random.randint(120, 290)
    second_ac = random.randint(120, 290)
    return [
        (f"abc{first_ac}_a", f"https://atcoder.jp/contests/abc{first_ac}/tasks/abc{first_ac}_a"),
        (f"abc{second_ac}_b", f"https://atcoder.jp/contests/abc{second_ac}/tasks/abc{second_ac}_b"),
        select_cf_prob(rating_groups[800])
    ]

def gen_med_match(rating_groups):
    return [
        select_cf_prob(rating_groups[800]),
        select_cf_prob(rating_groups[1000]),
        select_cf_prob(rating_groups[1200])
    ]

async def main():
    client_session = aiohttp.ClientSession(raise_for_status=True)

    pts_map = read_points()
    problems = await cfproblems(client_session)
    rating_groups = {}
    for prob in problems:
        if "rating" in prob:
            rat = prob["rating"]
            if rat in rating_groups:
                rating_groups[rat].append(prob)
            else:
                rating_groups[rat] = [prob]

    # print(await earliest_ac(client_session, "Noble_Mushtak", "abc180", "abc180_b"))
    # print(await earliest_cf(client_session, "Noble_Mushtak", 1637, "C"))
    
    if sys.argv[1] == "gen_pairs":
        groups = {}
        for username, info in pts_map.items():
            pts = info[2]
            if pts in groups:
                groups[pts].append(username)
            else:
                groups[pts] = [username]
        with open("pairs.txt", "w") as file:
            for pts, group in groups.items():
                print(f"{pts}-point group:")
                random.shuffle(group)
                for i in range(0, len(group), 2):
                    if i+1 == len(group):
                        print(f"{group[-1]} gets a bye!")
                        pts_map[group[-1]] = (pts_map[group[-1]][0], pts_map[group[-1]][1], pts_map[group[-1]][2]+1)
                    else:
                        print(f"{group[i]} will duel {group[i+1]}!")
                        print(group[i], group[i+1], "beg", file=file)

    if sys.argv[1] == "gen_matches":
        with open("pairs.txt", "r") as file:
            with open("matches.txt", "w") as file2:
                for line in file:
                    if line == "":
                        continue
                    user1, user2, mode = line.split()
                    if mode == "beg":
                        probs = gen_beg_match(rating_groups)
                    else:
                        probs = gen_med_match(rating_groups)
                    tags = [prob[0] for prob in probs]
                    print(user1, user2, " ".join(tags), file=file2)
                    
                    print(f"{user1} vs. {user2}:")
                    for _, link in probs:
                        print(link)
                        
    if sys.argv[1] == "upd_matches":
        with open("matches.txt", "r") as file:
            for line in file:
                if line == "":
                    continue
                toks = line.split()
                user1, user2 = toks[0], toks[1]
                # Tuple represents username, points, and latest submission time
                users = [(user1, 0, None), (user2, 0, None)]
                points = [100, 200, 300]
                for i, tag in enumerate(toks[2:]):
                    for i, user in enumerate(users):
                        if tag[:3] == "abc":
                            contest_id = tag.split("_")[0]
                            solve_time = await earliest_ac(client_session, pts_map[user[0]][0], contest_id, tag)
                        else:
                            contest_id, task_id = tag.split("-")
                            contest_id = int(contest_id)
                            solve_time = await earliest_cf(client_session, pts_map[user[0]][1], contest_id, task_id)
                        if solve_time != None:
                            print(f"{solve_time}: {user[0]} solved {tag} for {points[i]} points!")
                            new_points = user[1]+points[i]
                            new_datetime = user[2]
                            if user[2] == None or user[2] < solve_time:
                                new_datetime = solve_time
                            users[i] = (user[0], new_points, new_datetime)

                winner = None
                if users[0][1] == 0 and users[1][1] == 0:
                    print(f"Neither {user1} nor {user2} won their match!")
                elif users[0][1] > users[1][1] or (users[0][1] == users[1][1] and users[0][2] < users[1][2]):
                    print(f"{user1} won their match against {user2}!")
                    winner = user1
                else:
                    print(f"{user2} won their match against {user1}!")
                    winner = user2
                if winner != None:
                    pts_map[winner] = (pts_map[winner][0], pts_map[winner][1], pts_map[winner][2]+1)
                    
    write_points(pts_map)
    
    await client_session.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

import requests
import json
from pprint import pprint
from tor import Network
import traceback
import queue
import sqlite3
import random
import time

from user_agent import generate_user_agent

class Github:

    def req(self, url):
        print(url)
        response = None
        out = None

        while response is None:
            try:
                headers = {'User-Agent': generate_user_agent()}
                req = requests.get(url, headers=headers)
                response = req.content
                api_response = response.decode("utf-8")
                out = json.loads(api_response)
                if isinstance(out, dict) and out.get('message', "")[:23] == "API rate limit exceeded":
                    response = None
                    self.network.switch_ip()
            except:
                traceback.print_exc()
                self.network.switch_ip()
                time.sleep(random.randint(120, 180))
        time.sleep(random.randint(120, 180))
        return out

    def get_friends(self):
        url = "https://api.github.com/users/{0}/followers".format(self.user)
        subscribs = [elem["login"] for elem in self.req(url)]
        url = "https://api.github.com/users/{0}/following".format(self.user)
        subscribs += [elem["login"] for elem in self.req(url)]
        return subscribs

    def get_repos_info(self):
        url = "https://api.github.com/users/{0}/repos".format(self.user)
        data = self.req(url)

        fetch_data = [{'stars': elem['stargazers_count'],
                       'watchers': elem['watchers_count'],
                       'forks': elem['forks_count'],
                       'commits': len(self.req(elem['commits_url'][:-6])),
                       'languages': self.req(elem['languages_url'])} for elem in data
                      if elem.get("message", "") != "Git Repository is empty."]

        languages = [elem['languages'].keys() for elem in fetch_data]
        language_dicts = [elem['languages'] for elem in fetch_data]
        all_languages = set().union(*languages)
        summarized_languages = {prop: 0 for prop in all_languages}

        for language in language_dicts:
            for prop in language:
                summarized_languages[prop] += language[prop]

        self.data.update({
            'forks': sum([elem['forks'] for elem in fetch_data]),
            'watchers': sum([elem['watchers'] for elem in fetch_data]),
            'commits': sum([elem['commits'] for elem in fetch_data]),
            'stars': sum([elem['stars'] for elem in fetch_data]),
            'languages': str(summarized_languages)
        })

    def get_basic_info(self):
        api_req = "https://api.github.com/users/"
        url = "{0}{1}".format(api_req, self.user)
        data = self.req(url)

        self.data = {
            "user": self.user,
            "email": data.get('email', ""),
            "avatar": data.get('avatar_url', ""),
            "location": data.get('location', ""),
            "name": data.get('name', ""),
            "blog": data.get('blog', ""),
        }

    def __init__(self, user):
        self.network = Network()
        self.network.init_tor('supersafe') #, self.network.print_bootstrap_lines)
        self.user = user
        self.data = {}
        self.get_basic_info()
        self.get_repos_info()
        self.network.kill_tor()


def main():
    q = queue.Queue()
    q.put("TheBits")
    q.put("samdark")
    conn = sqlite3.connect('data/profiles.db')
    c = conn.cursor()
    i = 0

    while not q.empty() and i <= 100000:
        user = q.get()
        n = len(list(c.execute("""
            SELECT * FROM github WHERE user LIKE "{0}"
        """.format(user))))
        if n == 0:
            github = Github(user)

            for user in github.get_friends():
                q.put(user)

            pprint(github.data)

            c.execute("""
                INSERT INTO pages (
                user,
                email,
                avatar,
                location,
                name,
                blog,
                commits,
                watchers,
                stars,
                languages) VALUES
                ("{user}",
                "{email}",
                "{avatar}",
                "{location}",
                "{blog}",
                {commits},
                {watchers},
                {stars},
                "{languages}"
                )
                """.format(**github.data))
        i += 1

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
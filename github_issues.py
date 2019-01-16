from dateutil import parser
import requests
import datetime
import json

issues_content = dict()

class generate_gh_issue_report(object):

    def __init__(self, urls):
        self.urls = urls

    def get_api_response(self):
        ''' Takes the github url as an argument and return the json response if the status code is clear if not then None is returned '''
        headers = {'Accept': 'application/vnd.github.v3+json',
                   'User-Agent': 'Mozilla/5.0',
                   'Content-Type': 'application/json'}
        for url in self.urls:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_response = json.loads(response.content)
            else:
                json_response = None
            self.issue_information(json_response)

    def issue_information(self, json_results):
        '''Gets the information for each issue and stores it in global dictionary, takes json from the urls as an argument'''
        global issues_content
        key_dict = ["id", "state", "title", "repository_url", "created_at"]
        tag_content = dict()
        if json_results is not None:
            for issue in json_results:
                for tag, content in issue.items():
                    if tag in key_dict:
                        tag_content.update({tag: content})
                issues_content.update({issue['created_at']: tag_content})
                tag_content = dict()

    def sort_issues_by_date(self, dict_to_sort):
        '''Sort dictionary values according to the keys
        Returns sorted list based on date oldest to newest
        Takes a dictionary as an argument'''
        issues_list = [value for (key, value) in sorted(dict_to_sort.items())]
        return issues_list

    def find_top_date(self):
        '''Finds date with the most issues and returns dictionary value'''
        date_count = dict()
        for entry in issues_content:
            date = datetime.datetime.strftime(parser.parse(entry['created_at']), '%Y-%m-%d')
            if date not in date_count:
                date_count[date] = 1
            else:
                date_count[date] += 1
        date_with_most = sorted(list(date_count), key=date_count.__getitem__)[-1]
        return {"day": date_with_most}

    def get_occurrences(self, top_day):
        '''Gets the repositories in which the issues occurred and returns the dictionary value
        Takes the date with the most issues as an argument'''
        repo_count = dict()
        for entry in issues_content:
            if entry['repository_url'] not in repo_count:
                repo_count[entry['repository_url']] = 0
            if top_day['day'] in entry['created_at']:
                if entry['repository_url'] in repo_count:
                    repo_count[entry['repository_url']] += 1
        return repo_count

    def generate_result(self, top_day, occurrence_entries):
        '''Generates the desired output
        Takes the date with the most issues along with the repositories in which they occurred'''
        top_day.update({"occurrences": occurrence_entries})
        top_day_dict = {"top_day": top_day}
        issues_dict = {"issues": issues_content}
        issues_dict.update(top_day_dict)
        print(issues_dict)



def test_result():
    '''Test function to test output'''
    global issues_content
    api_urls = []
    git_hub_api_url_base = "https://api.github.com/"
    github_urls = ["https://api.github.com/repos/alexkimxyz/nsfw_data_scrapper/issues",
                   "repos/kamranahmedse/developer-roadmap/issues", "https://api.github.com/repos/sharkdp/hexyl/issues"]

    for gh_url in github_urls:
        if git_hub_api_url_base in gh_url:
            api_urls.append(gh_url)
        else:
            api_urls.append(git_hub_api_url_base + gh_url)

    issue_rep = generate_gh_issue_report(api_urls)

    issue_rep.get_api_response()

    issues_content = issue_rep.sort_issues_by_date(issues_content)
    top_day = issue_rep.find_top_date()
    occurrence_entries = issue_rep.get_occurrences(top_day)
    issue_rep.generate_result(top_day, occurrence_entries)


if __name__ == "__main__":
    test_result()
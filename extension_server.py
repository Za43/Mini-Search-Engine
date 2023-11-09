# this imports the SimpleServer library
import SimpleServer
# This imports the functions you defined in searchengine.py
from searchengine import create_index, search, textfiles_in_dir
# has the json.dumps function. So useful
import json

"""
File: extension_server.py
---------------------
Starts a server that takes in a search and displays a title, hyperlink,
and snippet of files containing the search
"""

# the directory of files to search over
DIRECTORY = 'bbcnews'
# perhaps you want to limit to only 10 responses per search..
MAX_RESPONSES_PER_REQUEST = 10


class SearchServer:
    def __init__(self):
        """
        load the data that we need to run the search engine. This happens
        once when the server is first created.
        """
        self.html = open('extension_client.html').read()
        self.index = {}
        self.file_titles = {}
        filenames = textfiles_in_dir(DIRECTORY)
        create_index(filenames, self.index, self.file_titles)

    # this is the server request callback function. You can't change its name or params!!!
    def handle_request(self, request):
        """
        This function gets called every time someone makes a request to our
        server. To handle a search, look for the query parameter with key "query"
        """
        # it is helpful to print out each request you receive!
        print(request)

        # if the command is empty, return the html for the search page
        if request.command == '':
            return self.html

        # if the command is search, the client wants you to perform a search!
        if request.command == 'search':
            search_item = request.get_params()['query'].lower()

            # finds files corresponding to the search
            file_list = search(self.index, search_item)
            title_lst = []

            # displays up to ten articles with title, url, and snippet
            for file in file_list:
                if len(title_lst) == MAX_RESPONSES_PER_REQUEST:
                    break
                snippet = get_snippet(file, search_item)
                title_dict = {'title': self.file_titles[file], 'url': file, 'snippet': snippet}
                title_lst.append(title_dict)
            return json.dumps(title_lst, indent=2)

        # when trying to get url to file
        if 'bbcnews' in request.command:
            correct_filename = request.get_command().replace('s', 's/')
            contents = open(correct_filename).read()
            return contents


def get_snippet(file_name, query):
    """
    Returns snippet of file containing first sentence, then next appearance of
    first word in search (if there is one). Limits both to 100 characters each
    """
    snippet = ''
    with open(file_name) as f:
        snippet = get_first_part(f, snippet)
        query = query.split()
        for line in f:

            # grabs sentence with first word of search in name
            if query[0] in line.lower():
                snippet = get_second_part(line, query[0], snippet)
                break
    return snippet


def get_first_part(f, snippet):
    """
    Gets the sentence of the article to add to the snippet,
    but limits to 100 characters. Returns updated snippet
    """
    # skips title and blank line
    f.readline()
    f.readline()

    first_sent = f.readline()
    first = first_sent.find('.')

    # if its greater than 100 characters, it stops it at the next space
    if first > 100:
        first = first_sent.find(' ', 100)
    snippet += first_sent[:first] + "... "
    return snippet


def get_second_part(line, query, snippet):
    """
    Creates second part of snippet by finding first word
    in search query and grabbing the rest of the sentence,
    adding it to snippet. Limits to 100 characters and returns snippet
    """
    word_index = line.lower().find(query)
    end = line.find('.', word_index)

    # stops at next space if > 100 characters again
    if end - word_index > 100:
        end = line.find(' ', word_index + 100)
    snip = line[word_index: end]
    snippet += snip + "..."
    return snippet


def main():
    # make an instance of your Server
    handler = SearchServer()
    # start the server to handle internet requests!
    SimpleServer.run_server(handler, 8000) # make the server


if __name__ == '__main__':
    main()

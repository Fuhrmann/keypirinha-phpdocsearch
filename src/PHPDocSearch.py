# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
from .ClassSuggestion import ClassSuggestion
from .FunctionSuggestion import FunctionSuggestion
from .Suggestion import Suggestion
import json
from datetime import datetime

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from bs4 import BeautifulSoup


class PHPDocSearch(kp.Plugin):
    """
    Search and open php doc pages.
    """
    # The php documentation website
    PHPDOC_WEBSITE = 'http://php.net'

    # The path to the URL used to get the documentation index
    PHPDOC_SEARCHINDEX_URL = '/js/search-index.php'

    # The name of the file inside cache folder used to save the search index from php.net website
    INDEX_FILENAME = 'searchindex.json'

    # Number of days the documentation index should be updated
    DAYS_KEEP_CACHE = 7

    def __init__(self):
        super().__init__()
        self.doc_index = []

    def on_start(self):
        self.generate_search_index()
        self.get_documentation_index()
        self.create_actions()
        pass

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="PHP Documentation",
                short_desc="Search for functions, classes and more in the official PHP documentation",
                target="phpdoc",
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
            return

        if len(user_input) > 0 and self.should_terminate(0.250):
            return

        mylist = self.filterbyvalue(self.doc_index, user_input)
        if (len(mylist)):
            self.set_suggestions(mylist, kp.Match.ANY, kp.Sort.LABEL_ASC)

    def filterbyvalue(self, seq, value):
        return list(filter(lambda item: value.lower() in item.label().lower(), seq))

    def on_execute(self, item, action):
        data_bag = item.data_bag().split('|')
        url_to_open = "http://php.net/manual/en/{}.php".format(data_bag[0])

        # Open in the browser
        if ((action and action.name() == 'open_url') or not action):
            kpu.web_browser_command(private_mode=None, new_window=None, url=url_to_open, execute=True)
            return

        # Copy its signature
        if (action and (action.name() in ['copy_signature'])):
            opener = kpnet.build_urllib_opener()
            with opener.open(url_to_open) as request:
                response = request.read()

            soup = BeautifulSoup(response, 'html.parser')

            if (action.name() == 'copy_signature'):
                param_elements = soup.findAll("div", {"class": "methodsynopsis"})
                params = ', '.join(param.get_text() for param in param_elements)
                params = params.replace('\n', '')
                kpu.set_clipboard(params)
                self.log("Signature copied!")
        return

    # Create the default actions to the suggestions
    def create_actions(self):
        general_actions = [
            self.create_action(name="open_url", label="Open in php.net", short_desc="Open the documentation in php.net")
        ]

        function_actions = [
            self.create_action(name="copy_signature", label="Copy signature", short_desc="Copy the function signature")
        ]

        self.set_actions(FunctionSuggestion.ITEMCAT, function_actions + general_actions)
        self.set_actions(ClassSuggestion.ITEMCAT, general_actions)

    # Download the search index from php.net website and write it to plugin's cache folder
    def generate_search_index(self):
        search_index_filepath = self.get_search_index_path()

        should_generate = False
        try:
            last_modified = datetime.fromtimestamp(os.path.getmtime(search_index_filepath)).date()
            if ((last_modified - datetime.today().date()).days > self.DAYS_KEEP_CACHE):
                should_generate = True
        except Exception as exc:
            should_generate = True

        if not should_generate:
            return False

        try:
            opener = kpnet.build_urllib_opener()
            with opener.open("{}{}".format(self.PHPDOC_WEBSITE, self.PHPDOC_SEARCHINDEX_URL)) as request:
                response = request.read()
        except Exception as exc:
            self.err("Could not reach the php documentation website to generate documentation index: ", exc)

        data = json.loads(response)
        with open(search_index_filepath, "w") as index_file:
            json.dump(data, index_file, indent=2)

    # Read the file containing the documentation index
    def get_documentation_index(self):
        if not self.doc_index:
            with open(self.get_search_index_path(), "r") as index_file:
                data = json.loads(index_file.read())
                for key in data:
                    label = data[key][0]
                    description = data[key][1]
                    section_type = data[key][2]

                    doc = self.get_documentation_type(label, description, key, section_type)
                    suggestion = self.create_item(
                        category=doc.ITEMCAT,
                        label=doc.label,
                        short_desc=doc.desc,
                        target=doc.label,
                        data_bag="{}|{}".format(doc.url, doc.section_type),
                        args_hint=kp.ItemArgsHint.FORBIDDEN,
                        hit_hint=kp.ItemHitHint.IGNORE
                    )

                    self.doc_index.append(suggestion)

        return self.doc_index

    # Returns the complete path of the file used as cache to the php documentation search index
    def get_search_index_path(self):
        cache_path = self.get_package_cache_path(True)
        return os.path.join(cache_path, self.INDEX_FILENAME)

    def get_documentation_type(self, label, description, url, section_type):
        for cls in Suggestion.__subclasses__():
            if cls.has_section_type(section_type):
                return cls(label, description, url, section_type)
        raise ValueError

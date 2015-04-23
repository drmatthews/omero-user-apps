
# Tool for developing regexes to use with OMERO.web to exclude blockedUrls from public access.
# To use, edit the regex.
# Add or remove urls you want to test from the list then run...
# It will print a statement you can use to configure OMERO with the regex you've used

# You may also want to remove the ability of visitors to switch user in the drop-down menu
# $ bin/omero config set omero.web.ui.menu.dropdown '{}'

import re

# All these example urls should be blocked (search should return None)
# Either because they create data for the public user or they are resource-intensive
blockedUrls = ['/webadmin/',                    # Don't allow user to edit their own profile
        '/webclient/logout/',                   # If public user goes to logout, redirect to login
        '/webclient/action/addnewcontainer/',   # Block Project/Dataset creation
        '/webclient/annotate_tags/?dataset=3',  # Don't allow annotations (even in read-ann group)
        '/webclient/annotate_rating/',
        '/webclient/script_ui/8/',              # Disable dialog for running scripts
        '/webclient/ome_tiff_info',             # OME-TIFF export dialog... 
        '/webclient/ome_tiff_script/63',        # ...and script should be disabled
        '/webclient/figure_script/Thumbnail/?Image=63',      # Script UIs for figures
        '/webgateway/archived_files/',           # Optional: disable download of original files
        '/webgateway/download_as/']              # Optional: disable batch export of PNG, JPEG, TIFF

# All other /webclient/ urls should be allowed for example...
allowedUrls = ['/webclient/',
               '/webclient/load_data/']


url_filter = '^/(?!webadmin' \
        '|webclient/' \
            '(action' \
            '|logout' \
            '|annotate_(file|tags|comment|rating|map)' \
            '|script_ui' \
            '|ome_tiff' \
            '|figure_script' \
            ')' \
        '|webgateway/' \
            '(archived_files' \
            '|download_as' \
            ')' \
        ')'


p = re.compile(url_filter)

print "\n", "bin/omero config set omero.web.public.url_filter '%s'" % url_filter, "\n"

for url in blockedUrls:
    print url
    assert p.search(url) is None

for url in allowedUrls:
    print url
    assert p.search(url) is not None

GITHUB_BASE_URL = "https://github.com"
GITHUB_BASE__API_URL = "https://api.github.com/repos"
GITHUB_URL_PATTERN = (
    GITHUB_BASE_URL
    + r"/(?P<username>[^/]+)/(?P<repo>[^/]+)(?:(?:/blob|/tree)/(?P<branch>[^/]+)/(?P<path>[^#]*))?(?:#L(?P<start_line>\d+)(?:-L(?P<end_line>\d+))?)?(?:/issues/(?P<issue_number>\d+))?$"
)

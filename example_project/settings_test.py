from .settings import *  # noqa
from .settings import BASE_DIR

# DEBUGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore # noqa F405

# django-webpack-loader
# ------------------------------------------------------------------------------
# VERY SPECIAL - has a FakeWebpackLoader class for all cases
# EXCEPT - specific tests, we can override the LOADER_CLASS and make it use
# the real WebpackLoader class.
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles_test/",
        "CACHE": False,
        "STATS_FILE": BASE_DIR + "/example_project/webpack/webpack-stats-test.json",
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loaders.FakeWebpackLoader",
    }
}

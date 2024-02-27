import hashlib
import logging
import os
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


class CompileAssetsOnChangeMixin:
    CACHE_FILE = "bundles_test_hash.cache"

    @classmethod
    def setUpClass(cls):
        # Compile assets if missing or changed
        directory_paths = [
            Path(settings.ROOT_DIR, "apps", "static", "js"),
            Path(settings.ROOT_DIR, "apps", "static", "css"),
        ]

        hash_value = cls._check_directories_for_changes(directory_paths)
        if cls._has_hash_changed(hash_value):
            cls._webpack_compile()

        super().setUpClass()

    @classmethod
    def _has_hash_changed(cls, hash_value):
        """Check if the hash value has changed since the last run."""
        cache_file_path = Path(settings.ROOT_DIR, "example_project", "static", "bundles_test", cls.CACHE_FILE)

        try:
            with open(cache_file_path) as f:
                cached_hash = f.read()
            if hash_value == cached_hash:
                return False
        except FileNotFoundError:
            pass

        # Cache the current hash value to a file
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as f:
            f.write(hash_value)

        return True

    @classmethod
    def _check_directories_for_changes(cls, directories):
        """Check if the hash value of the directories has changed, and run _webpack_compile if it has."""
        hasher = hashlib.sha256()
        for directory in directories:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        hasher.update(cls._get_file_hash(filepath).encode("utf-8"))
        return hasher.hexdigest()

    @classmethod
    def _get_file_hash(cls, filename):
        """Calculate the SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filename, "rb") as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    @classmethod
    def _webpack_compile(cls):
        logger.debug("Compiling Webpack Assets...")

        os.system("yarn run build_test")


class UseRealWebpackmixin(CompileAssetsOnChangeMixin):
    @classmethod
    def setUpClass(cls):
        cls._switch_to_real_webpack_loader()

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls._switch_back_to_orig_webpack_loader()

        super().tearDownClass()

    @classmethod
    def _switch_to_real_webpack_loader(cls):
        from webpack_loader import utils

        cls.old_loader = utils.get_loader

        def new_loader(config_name):
            config = utils.load_config(config_name)
            loader_class = utils.import_string("webpack_loader.loader.WebpackLoader")
            return loader_class(config_name, config)

        utils.get_loader = new_loader

    @classmethod
    def _switch_back_to_orig_webpack_loader(cls):
        from webpack_loader import utils

        utils.get_loader = cls.old_loader

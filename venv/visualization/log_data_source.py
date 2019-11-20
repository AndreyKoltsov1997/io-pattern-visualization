import os

class LogDataSource:

    def __init__(self, source_file_path, source_description):
        if not os.path.exists(source_file_path):
            raise Exception(f"Path {source_file_path} doesn't exist.")
        self.source_file_path = source_file_path
        self.source_description = source_description

    def get_source_description(self) -> str:
        return self.source_description

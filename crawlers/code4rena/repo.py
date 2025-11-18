from ..base.repo import RepoCrawlerBase, RepoCrawlerBaseConfig
from configs.code4rena.report import REPORT_DATA_PATH
from configs.code4rena.repo import GITHUB_REPO_DATA_DIR_PATH


class RepoCrawler(RepoCrawlerBase):
    def __init__(self, token: str, root_dir: str):
        config = RepoCrawlerBaseConfig(
            token=token,
            root_dir=root_dir,
            report_dir_path=REPORT_DATA_PATH.split("{name}")[0].format(
                root_dir=root_dir
            ),
            repo_data_dir_path=GITHUB_REPO_DATA_DIR_PATH.format(root_dir=root_dir),
        )
        super().__init__(config)

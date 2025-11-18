import argparse
import os
from analyzers.base.analyzer import AnalyzerBase
from configs.base.types import Platform


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--platform",
        type=str,
        required=True,
        help="Platform to crawl projects from",
    )
    return parser.parse_args()


def analyzer_instance(platform: str, root_dir: str) -> AnalyzerBase:
    print(f"Creating analyzer for {platform}\n")
    module_path = f"analyzers.{platform.lower()}.analyzer"
    class_name = "Analyzer"
    module = __import__(module_path, fromlist=[class_name])
    analyzer_class = getattr(module, class_name)
    return analyzer_class(root_dir)


def analyzer_factory(platform: str, root_dir: str) -> list[AnalyzerBase]:
    ## initialize the list of types and platforms
    platfroms = [p.value.lower() for p in Platform]
    platform = platform.lower()
    analyzers = []
    if platform == "all":
        for platform in platfroms:
            analyzer = analyzer_factory(platform, root_dir)
            analyzers.append(analyzer[0])
    else:
        if platform not in platfroms:
            raise ValueError(f"Platform must be in {platfroms}")
        analyzer = analyzer_instance(platform, root_dir)
        analyzers.append(analyzer)
    return analyzers


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    args = parse_args()
    analyzers = analyzer_factory(args.platform, root_dir)
    for analyzer in analyzers:
        analyzer.analyze()

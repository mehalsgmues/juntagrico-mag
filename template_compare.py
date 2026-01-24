import argparse
import logging
import re
import subprocess
import os
import textwrap
from functools import cached_property

logger = logging.getLogger(__name__)


MERGE_TOOL = "pycharm", "merge"
TEMPLATE_DIFF_DIR = ".template_diff"


def tag_regex(tag):
    return re.compile("{%\s*" + tag + "\s(.*?)\s*%}")


def suffix_filename(file_name, suffix):
    return ".".join(file_name.split(".")[:-1] + [suffix] + [file_name.split(".")[-1]])


def nested_named_groups(starts, ends):
    pairs = ()
    while starts and ends[0] > starts[0][1]:
        name, start = starts.pop(0)
        nested = nested_named_groups(starts, ends)
        pairs += ([name, start, ends.pop(0), nested],)
    return pairs


class TemplateHeader:
    EXTENDS_TAG = tag_regex("extends")
    LOAD_TAG = tag_regex("load")

    def __init__(self, extends=None, loads=None):
        self.extends = extends
        self.loads = loads or []

    def __str__(self):
        return "\n".join([self.extends or ''] + self.loads)

    @classmethod
    def from_string(cls, string):
        header = TemplateHeader()
        header.append(string)
        return header

    @cached_property
    def extends_path(self):
        if self.extends is None:
            return None
        return self.EXTENDS_TAG.search(self.extends).group(1).strip()

    def append(self, line):
        if m := self.EXTENDS_TAG.search(line):
            self.extends = m.group()
        for m in self.LOAD_TAG.finditer(line):
            self.loads.append(m.group())


class TemplateBlock:
    BLOCK_TAG = tag_regex("block")
    ENDBLOCK_TAG = tag_regex("endblock")
    SUPER_TAG = re.compile("{{\s*block.super\s*}}")

    def __init__(self, name, content : list = None):
        self.name = name
        self.content : list[str|TemplateBlock] = content or [""]

    @cached_property
    def blocks(self):
        """
        :return: dict of neste TemplateBlocks in this block
        """
        return {
            block.name: block
            for block in self.content
            if isinstance(block, TemplateBlock)
        }

    def get_block(self, name):
        if block := self.blocks.get(name):
            return block
        for block in self.blocks.values():
            if block := block.get_block(name):
                return block

    def __str__(self):
        return self.name + " - " + str(self.full_content.count("\n")) + " lines"

    @classmethod
    def from_nested_pairs(cls, nested_pairs, string, cursor=0):
        content = []
        for pair in nested_pairs:
            name, start, end, nested = pair
            if start > cursor:
                content.append(string[cursor:start])
                cursor = start
            if not nested:
                content.append(cls(name, [string[start:end]]))
                cursor = end
            else:
                block_content, cursor = cls.from_nested_pairs(nested, string[:end], cursor)
                content.append(cls(name, block_content))
        if cursor < len(string):
            content.append(string[cursor:])
            cursor = len(string)

        return content, cursor

    @classmethod
    def from_string(cls, string):
        """
        :returns: list of strings (around blocks) and TemplateBlock objects found in the given string.
        """
        starts = [(b.group(1), b.start()) for b in cls.BLOCK_TAG.finditer(string)]
        ends = [b.end() for b in cls.ENDBLOCK_TAG.finditer(string)]
        nested_pairs = nested_named_groups(starts, ends)
        content = cls.from_nested_pairs(nested_pairs, string)[0]
        return content

    @classmethod
    def parse_block_name(cls, line):
        return cls.BLOCK_TAG.search(line).group(1).strip()

    @property
    def full_content(self):
        text = ""
        indent = ""
        for content in self.content:
            if isinstance(content, TemplateBlock):
                text += textwrap.indent(content.full_content, indent).strip()
            elif isinstance(content, str):
                text += content
                indent = content.rpartition("\n")[2]
            else:
                text += "[BLOCK NOT FOUND!]"
        return text

    @cached_property
    def uses_super(self):
        for content in self.content:
            if isinstance(content, str):
                if self.SUPER_TAG.search(content) is not None:
                    return True
        return False

    def patch(self, template_file : 'TemplateFile'):
        new_block = TemplateBlock(self.name)
        if self.uses_super:
            base_block = self
        else:
            base_block = template_file.get_block(self.name)
        if base_block is None:
            return None
        indent = ""
        for content in base_block.content:
            if isinstance(content, str):
                new_block.content.append(content)
            elif isinstance(content, TemplateBlock):
                # use subblock from this block if found,
                # otherwise, pass empty block to let recursive call find the right version
                sub_block = self.get_block(content.name) or TemplateBlock(content.name)
                new_block.content.append(sub_block.patch(template_file))
            else:
                raise ValueError(f"Unexpected content type: {type(content)}")
        return new_block


class TemplateFile:
    def __init__(self, template_dir, template_path):
        self.template_dir = template_dir
        self.template_path = template_path
        self.file_path = template_dir + "/" + template_path

    def __str__(self):
        return self.file_path

    def exists(self):
        return os.path.exists(self.file_path)

    @cached_property
    def content(self):
        with open(self.file_path, "r") as f:
            content = f.read()
        return content

    @cached_property
    def headers(self):
        """
        :return: TemplateHeader of this template
        """
        return TemplateHeader.from_string(self.content)

    @cached_property
    def blocks(self):
        """
        :return: dict of top level TemplateBlocks in this template
        """
        blocks = TemplateBlock.from_string(self.content)
        return {
            block.name: block
            for block in blocks
            if isinstance(block, TemplateBlock)
        }

    def get_block(self, name):
        if block := self.blocks.get(name):
            return block
        for block in self.blocks.values():
            if block := block.get_block(name):
                return block
        if self.headers.extends:
            parent_template = TemplateFile(self.template_dir, self.headers.extends_path.strip('"'))  # TODO: deal with variables
            return parent_template.get_block(name)

    def write_blocks(self, blocks, headers=None, extends=None):
        target_file = TemplateFile(self.template_dir, suffix_filename(self.template_path, 'blocks'))
        headers = headers or self.headers
        if extends:
            headers = TemplateHeader(extends, headers.loads)
        with open(str(target_file), "w") as g:
            g.write(str(headers) + "\n")
            for name, block in blocks.items():
                g.write("\n")
                block = block.patch(self)
                g.write(block.full_content if block else "[BLOCK NOT FOUND!]")
                g.write("\n")
        return target_file


class Project:
    def __init__(self, host, owner, project, template_dir):
        self.project = project
        self.repo = f"{host}/{owner}/{project}.git"
        self.template_dir = template_dir
        self.base_version = None
        self.new_version = None

    def _get_dir(self, version):
        return f"{TEMPLATE_DIFF_DIR}/{self.project}/{version}"

    def fetch_version(self, branch):
        flat_branch = branch.replace("/", "_")
        target_dir = self._get_dir(flat_branch)
        if os.path.exists(target_dir):
            logger.info(f"Version {branch} already fetched")
            return flat_branch

        subprocess.run(
            ["git", "clone", "--verbose", "-n", "--depth=1", "--filter=tree:0", "-b" + branch, self.repo, target_dir]
        )
        subprocess.run(["git", "sparse-checkout", "set", "--no-cone", self.template_dir], cwd=target_dir)
        subprocess.run(["git", "checkout"], cwd=target_dir)
        logger.info(f"Fetched version {branch}")
        return flat_branch

    def set_base_version(self, branch):
        self.base_version = self.fetch_version(branch)

    def set_new_version(self, branch):
        self.new_version = self.fetch_version(branch)

    def compare(self, source_templates, file_path):
        my_version = TemplateFile(source_templates, file_path)
        base_version = TemplateFile(self._get_dir(self.base_version) + "/" + self.template_dir, file_path)
        new_version = TemplateFile(self._get_dir(self.new_version) + "/" + self.template_dir, file_path)

        # check if template is relevant in project and if it moved
        if base_version.exists:
            if not new_version.exists:
                # TODO: follow file renames
                logger.error(f"Template '{file_path}' not found in new version. It probably was moved.")
                return
        else:
            if new_version.exists:
                # TODO: cover case, where my template was already moved to new location and is then compared again.
                logger.error(f"Template '{file_path}' was added in new version and conflicts with your template.")
                return
            logger.info(f"Ignoring template '{file_path}', not found in project")
            return

        # only compare overwritten blocks if template extends itself
        extends = my_version.headers.extends_path
        if extends == '"' + file_path + '"':  # TODO: deal with relative paths
            logger.debug(f"template '{file_path}', extends itself, only compare blocks")
            blocks = my_version.blocks
            base_version = base_version.write_blocks(blocks, my_version.headers)
            new_version = new_version.write_blocks(blocks, extends=my_version.headers.extends)

        target_file = suffix_filename(file_path, 'new')
        subprocess.run([
            *MERGE_TOOL,
            str(my_version),
            str(new_version),
            str(base_version),
            source_templates + "/" + target_file
        ])


def main(template_path):
    # TODO: deal with templates from add-ons and non-juntagrico packages
    project = Project(
        host="https://github.com",
        owner="juntagrico",
        project="juntagrico",
        template_dir="/juntagrico/templates"
    )
    project.set_base_version("mag")
    project.set_new_version("releases/2.0")

    project.compare("mehalsgmues/templates", template_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="python -m template_compare",
        description="Compares template overrides (experimental)")
    parser.add_argument("template", help="relative path to template file or folder")
    args = parser.parse_args()
    main(args.template)

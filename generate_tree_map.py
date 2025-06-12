import os
import json

def generate_tree_map(root_path: str, indent: str = "├── ", last_indent: str = "└── ", spacer: str = "│   ", final_spacer: str = "    "):
    """
    Generate and print a tree-style directory map starting at the given root path.

    Args:
        root_path (str): The absolute or relative path to the directory to scan.
    """

    def walk_dir(curr_path: str, prefix: str = "", is_last: bool = False):
        entries = sorted(os.listdir(curr_path))
        entries = [e for e in entries if not e.startswith(".")]  # Skip hidden files

        for index, entry in enumerate(entries):
            full_path = os.path.join(curr_path, entry)
            is_entry_last = (index == len(entries) - 1)

            branch = last_indent if is_entry_last else indent
            line_prefix = prefix + branch
            next_prefix = prefix + (final_spacer if is_entry_last else spacer)

            if os.path.isdir(full_path):
                print(f"{line_prefix}{entry}/")
                walk_dir(full_path, next_prefix, is_entry_last)
            else:
                comment = comment_for_file(entry)
                print(f"{line_prefix}{entry} {comment}")

    def comment_for_file(filename: str) -> str:
        # Define special comment annotations
        special_comments = {
            "main.py": "◀ CLI entry point",
            "pyproject.toml": "◀ For installability (recommended)",
        }
        return f"◀ {special_comments[filename]}" if filename in special_comments else ""

    root_dir_name = os.path.basename(os.path.abspath(root_path))
    print(f"{root_dir_name}/")
    walk_dir(root_path)

# Example usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a directory tree map.")
    parser.add_argument("target", help="Path to the target directory")
    args = parser.parse_args()

    if os.path.isdir(args.target):
        generate_tree_map(args.target)
    else:
        print(f"Error: '{args.target}' is not a valid directory.")


def generate_tree_map_json(root_path: str, output_json_path: str = None):
    """
    Generate a tree-style map of the target directory and optionally save it to a .json file.

    Args:
        root_path (str): The absolute or relative path to the directory to scan.
        output_json_path (str, optional): If provided, saves the directory tree to this JSON file.
    """

    def walk_dir_json(curr_path: str):
        entries = sorted(os.listdir(curr_path))
        entries = [e for e in entries if not e.startswith(".")]  # Skip hidden

        tree = []
        for entry in entries:
            full_path = os.path.join(curr_path, entry)
            if os.path.isdir(full_path):
                subtree = walk_dir_json(full_path)
                tree.append({"type": "directory", "name": entry, "children": subtree})
            else:
                tree.append(
                    {"type": "file", "name": entry, "comment": comment_for_file(entry)}
                )
        return tree

    def print_tree(tree, prefix=""):
        for idx, node in enumerate(tree):
            is_last = idx == len(tree) - 1
            branch = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            if node["type"] == "directory":
                print(f"{prefix}{branch}{node['name']}/")
                print_tree(node["children"], next_prefix)
            else:
                comment = f" {node['comment']}" if node["comment"] else ""
                print(f"{prefix}{branch}{node['name']}{comment}")

    def comment_for_file(filename: str) -> str:
        special_comments = {
            "main.py": "◀ CLI entry point",
            "pyproject.toml": "◀ For installability (recommended)",
        }
        return special_comments.get(filename, "")

    if not os.path.isdir(root_path):
        raise ValueError(f"'{root_path}' is not a valid directory.")

    tree_structure = walk_dir_json(root_path)

    # Print tree to terminal
    root_name = os.path.basename(os.path.abspath(root_path))
    print(f"{root_name}/")
    print_tree(tree_structure)

    # Save to JSON if requested
    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump({"root": root_name, "structure": tree_structure}, f, indent=4)
        print(f"\n✅ Tree structure saved to {output_json_path}")

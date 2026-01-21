#! /usr/bin/env python

import os
import re
import sys
import hashlib
from collections import defaultdict


# flag to control if strip white characters from submissions 
DO_CLEAN = False

# minimum lines of file to be considered
MIN_LINES = 20

SUBMISSIONS_DIR = 'submissions'

LANGUAGES = ['c', 'cpp', 'js', 'java', 'py']

def normalize_content(filepath, min_lines, do_clean):
    """Read file, remove blanks and whitespace (diff -Bw style)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            sys.exit(0)
            return ''

    if do_clean:
        # Strip whitespace and remove blank lines
        cleaned = [
            ''.join(line.split())  # removes all spaces, tabs
            for line in lines
            if line.strip() != ''  # skip blank lines
        ]
    else:
        cleaned = lines

    if len(cleaned) < min_lines:
        cleaned = []
    return ''.join(cleaned)



def hash_file(content):
    """Compute SHA256 of normalized content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def collect_files(submissions_dir):
    file_dict = defaultdict(list)

    for lang in LANGUAGES:
        lang_path = os.path.join(submissions_dir, lang)
        if not os.path.isdir(lang_path):
            continue

        for task in os.listdir(lang_path):
            task_path = os.path.join(lang_path, task)
            if not os.path.isdir(task_path):
                continue

            for filename in os.listdir(task_path):
                if filename.endswith(f'.{lang}'):
                    filepath = os.path.join(task_path, filename)
                    file_dict[(lang, task)].append(filepath)

    return file_dict


def group_by_hash(file_list, min_lines, do_clean):
    """Group files that are identical after normalization."""

    hash_map = defaultdict(list)
    
    for filepath in file_list:
        content = normalize_content(filepath, min_lines, do_clean)
        if not content:
            continue
        h = hash_file(content)
        hash_map[h].append(filepath)

    clusters = [
        group for group in hash_map.values() if len(group) > 1
    ]

    return clusters



def check_duplicates(base_dir, min_lines, do_clean):

    submissions_dir = os.path.join(base_dir, "submissions")
    file_groups = collect_files(submissions_dir)

    csv = open(os.path.join(base_dir,"clusters.csv"),"w")

    global_idx = 0
    for (lang, task), files in file_groups.items():
        print(f'\n=== Checking {lang}/{task} ({len(files)} submissions) ===')
        pattern = re.compile(fr"^(\d+)-({task})-sub(\d+).{lang}")
        clusters = group_by_hash(files, min_lines, do_clean)

        if clusters:
            print(f'Found {len(clusters)} clusters of identical submissions:')
            for idx, cluster in enumerate(clusters, 1):
                global_idx += 1
                for filepath in sorted(cluster):
                    match = re.search(pattern,os.path.basename(filepath))
                    if not match:
                        continue
                    compet_id = match.groups()[0]
                    submission_id = match.groups()[2]
                    ############
                    # hack to make easier to show the submission as text
                    ############
                    name, ext = os.path.splitext(filepath)
                    name = name.replace('submissions','submissions_all')
                    new_filepath = f"{name}_{ext[1:]}.txt"
                    print(f"Cluster {global_idx},{task},{lang},{compet_id},{submission_id},{new_filepath}", file=csv)
        else:
            print('No identical submissions found.')


def main():
    try:
        submissions_dir = sys.argv[1]
    except:
        print(f"usage: {sys.argv[0]} submissions_dir")
        sys.exit(0)
    check_duplicates(submissions_dir)




if __name__ == '__main__':
    main()

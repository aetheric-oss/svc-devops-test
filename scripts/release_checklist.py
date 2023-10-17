#!/bin/python3

import glob
import re
from enum import Enum
from argparse import ArgumentParser

RED_X = "X"
GREEN_CHECK = "\U00002713"


def get_logs(filenames):
    statements = {}
    possible = ["info!", "error!", "warn!", "debug!", "println!", "panic!"]

    for fname in filenames:
        f = open(fname, 'r')
        in_tests = False
        gathered = ""
        gathering = False
        current_function = None

        i = 0
        for line in f.readlines():
            i += 1

            if "mod tests" in line or 'test' in fname:
                in_tests = True

            if any([x for x in possible if x in line]):
                gathering = True

            if "fn " in line:
                result = re.search(r"fn ([a-zA-Z_0-9]+)(<.*>)*\s*\(", line)
                if result:
                    current_function = result.group(1)
                else:
                    current_function = None

            if gathering:
                gathered += line

            if gathering and (");" in line):
                gathered = gathered.strip()
                gathered = re.sub(r"///\s*", "/// ", gathered)
                full = f'{fname} ({i}) - {gathered}'
                in_comments = True if re.search(r"\t*\s*//.*", line) else False
                statements[f'{fname} ({i})'] = {
                    "statement": gathered,
                    "tests": in_tests,
                    "comments": in_comments,
                    "function": current_function
                }
                gathering = False
                gathered = ""

    return statements


def check_log_statements(filenames, include_tests, include_comments):
    print("### \U0001F4E3 Checking log statements...\n")

    statements = get_logs(filenames)
    if not statements:
        print("All good! \U0001F389\n")
        return

    hidden_fields = False
    longest_key = max([len(x) for x in statements.keys()])
    fmt_string = '{:^4} | {:^3} | {:<{longest_key}} | {:<20} | {:<50}'
    print(fmt_string.format("Test", "///", "Location",
                            "Type", "Statement", longest_key=longest_key))
    print(fmt_string.format("-"*4, "-"*3, "-"*longest_key,
                            "-"*20, "-"*50, longest_key=longest_key))
    for key in statements.keys():
        if statements[key]["tests"] and not include_tests:
            hidden_fields = True
            continue

        if statements[key]["comments"] and not include_comments:
            hidden_fields = True
            continue

        stmt = statements[key]["statement"].replace('\n', '')
        sub = re.search('"([^"]*)"', statements[key]["statement"]).group(1)

        if re.search(r"\([a-zA-Z_0-9\-\(\)\:\s]+\)", sub) is None:
            print(fmt_string.format(
                GREEN_CHECK if statements[key]["tests"] else RED_X,
                GREEN_CHECK if statements[key]["comments"] else RED_X,
                key,
                "(no_fn_prepend) msg",
                (stmt[0:47] + '...') if len(stmt) > 50 else stmt,
                longest_key=longest_key
            ))
        elif "({})".format(statements[key]["function"]) not in sub:
            print(fmt_string.format(
                GREEN_CHECK if statements[key]["tests"] else RED_X,
                GREEN_CHECK if statements[key]["comments"] else RED_X,
                key,
                "wrong (fn prepend)",
                stmt[0:50],
                longest_key=longest_key
            ))

        if re.search(r".*[.?!(\{\})(\{:\?})]+$", sub) is None:
            print(fmt_string.format(
                GREEN_CHECK if statements[key]["tests"] else RED_X,
                GREEN_CHECK if statements[key]["comments"] else RED_X,
                key,
                "punctuation",
                stmt[0:50],
                longest_key=longest_key
            ))

    if hidden_fields:
        print("\n(Some fields hidden. Use -t and -c to show hidden fields.)")


def get_dead_code(filenames):
    statements = {}

    for fname in filenames:
        f = open(fname, 'r')

        gathered = ""
        gathering = False

        i = 0
        for line in f.readlines():
            i += 1
            if 'dead_code' in line:
                gathering = True
                continue

            key = ""

            if gathering and ("fn " in line):
                gathered = re.search(
                    r"(fn [a-zA-Z_0-9]+)(<.*>)*\s*\(", line).group(1)
                key = f'{fname} ({i})'

            if gathering and (" enum " in line):
                gathered = re.search(
                    r"(enum [a-zA-Z_0-9]+).*\{", line).group(1)
                key = f'{fname} ({i})'

            if gathering and (" struct " in line):
                gathered = re.search(
                    r"(struct [a-zA-Z_0-9]+).*\{", line).group(1)
                key = f'{fname} ({i})'

            if gathering and (" mod " in line):
                gathered = re.search(r"(mod [a-zA-Z_0-9]+)", line).group(1)
                key = f'{fname} ({i})'

            if gathering and (" impl " in line):
                gathered = re.search(r"(impl [a-zA-Z_0-9]+)", line).group(1)
                key = f'{fname} ({i})'

            if key:
                statements[key] = gathered
                gathering = False
                gathered = ""

    return statements


def check_dead_code(filenames):
    print("### \U0001F480 Checking #[allow(dead_code)]...\n")

    statements = get_dead_code(filenames)
    if not statements:
        print("All good! \U0001F389\n")
        return

    longest_key = max([len(x) for x in statements.keys()])

    fmt_string = '{:<{longest_key}} | {:<60}'
    print(fmt_string.format("Location", "Statement", longest_key=longest_key))
    print(fmt_string.format("-"*longest_key, "-"*60, longest_key=longest_key))
    for key in statements.keys():
        print(fmt_string.format(
            key.ljust(longest_key, ' '),
            statements[key],
            longest_key=longest_key
        ))


def get_unwraps(filenames):
    statements = {}
    for fname in filenames:
        f = open(fname, 'r')

        gathered = ""
        gathering = False
        in_tests = False
        i = 0
        for line in f.readlines():
            in_comment = False
            i += 1

            if 'mod test' in line or 'test' in fname:
                in_tests = True

            if 'unwrap()' in line:
                key = f'{fname} ({i})'

                if re.search(r"\t*\s*//.*", line):
                    in_comment = True

                statements[key] = {
                    "tests": in_tests,
                    "comments": in_comment
                }

            if '.expect' in line:
                key = f'{fname} ({i})'

                if re.search(r"\t*\s*//.*", line):
                    in_comment = True

                statements[key] = {
                    "tests": in_tests,
                    "comments": in_comment
                }

    return statements


def check_unwraps(filenames, include_tests, include_comments):
    print("### \U0001F380 Checking unwraps and .expect() calls...\n")
    statements = get_unwraps(filenames)

    if not statements:
        print("All good! \U0001F389\n")
        return

    hidden_fields = False

    fmt_string = '{:^5} | {:^3} | {:<60}'
    print(fmt_string.format("Test", "///", "Location"))
    print(fmt_string.format("-"*5, "-"*3, "-"*60))
    for key in statements.keys():
        if statements[key]["tests"] and not include_tests:
            hidden_fields = True
            continue

        if statements[key]["comments"] and not include_comments:
            hidden_fields = True
            continue

        print(fmt_string.format(
            GREEN_CHECK if statements[key]["tests"] else RED_X,
            GREEN_CHECK if statements[key]["comments"] else RED_X,
            key
        ))

    if hidden_fields:
        print("\n(Some fields hidden. Use -t and -c to show hidden fields.)")


def separator():
    print("{}\n".format("-"*80))


def get_todo_items(filenames):
    statements = {}
    for fname in filenames:
        f = open(fname, 'r')

        gathered = ""
        gathering = False
        in_tests = False
        i = 0
        for line in f.readlines():
            i += 1

            if 'mod test' in line or 'test' in fname:
                in_tests = True

            if 'TODO' in line or 'FIXME' in line or ':construction' in line:
                key = f'{fname} ({i})'

                statement = line.strip().replace('\n', '')
                statement = statement.replace(r"\s+", r"\s")
                statements[key] = {
                    "statement": statement,
                    "tests": in_tests
                }

    return statements


def check_todo_items(filenames, include_tests):
    print("### \U0001F6A7 Checking TODO items and FIXMEs...\n")
    statements = get_todo_items(filenames)

    if not statements:
        print("All good! \U0001F389\n")
        return

    hidden_fields = False
    longest_key = max([len(x) for x in statements.keys()])
    fmt_string = '{:^5} | {:<{longest_key}} | {:<50}'
    print(fmt_string.format("Test", "Location",
                            "Statement", longest_key=longest_key))
    print(
        fmt_string.format(
            "-"*5, "-"*longest_key, "-"*50,
            longest_key=longest_key
        )
    )
    for key in statements.keys():
        if statements[key]["tests"] and not include_tests:
            hidden_fields = True
            continue

        statement = statements[key]["statement"]
        print(fmt_string.format(
            GREEN_CHECK if statements[key]["tests"] else RED_X,
            key,
            statement if len(statement) < 50 else statement[0:47] + '...',
            longest_key=longest_key
        ))

    if hidden_fields:
        print("\n(Some fields hidden. Use -t and -c to show hidden fields.)")
    print("\nEnd - Check Todo Items")


def get_cargo_toml(filenames):
    statements = {}
    for fname in filenames:
        f = open(fname, 'r')

        gathered = ""
        gathering = False
        i = 0
        for line in f.readlines():
            i += 1

            result = re.search(r"[0-9]+\.[0-9]+\.[0-9]+", line)
            if ('develop' not in line) and result:
                key = f'{fname} ({i})'
                statement = line.strip().replace('\n', '')
                statement = statement.replace(r"\s+", r"\s")
                statements[key] = {
                    "statement": statement
                }

    return statements


def check_cargo_toml(filenames):
    print("### \U0001F5C3 Checking Cargo.toml versions...\n")
    statements = get_cargo_toml(filenames)

    if not statements:
        print("All good! \U0001F389\n")
        return

    longest_key = max([len(x) for x in statements.keys()])
    fmt_string = '{:<{longest_key}} | {:<50}'
    print(fmt_string.format("Location", "Statement", longest_key=longest_key))
    print(fmt_string.format("-"*longest_key, "-"*50, longest_key=longest_key))
    for key in statements.keys():
        statement = statements[key]["statement"]
        print(fmt_string.format(
            key,
            statement if len(statement) < 50 else statement[0:47] + '...',
            longest_key=longest_key
        ))


if __name__ == "__main__":
    print("\n## Release Checklist\n")

    parser = ArgumentParser()
    parser.add_argument(
        "-t", "--include-tests",
        dest="tests",
        action="store_true",
        help="Include test sections and files in checks"
    )
    parser.add_argument(
        "-c", "--include-comments",
        dest="comments",
        action="store_true",
        help="Include comments in checks"
    )
    args = parser.parse_args()

    # .rs Files
    filenames = glob.glob("**/*.rs", recursive=True)
    filenames = [
        x for x in filenames if (
            "target/" not in x
            and "build/" not in x
            and "registry/" not in x
        )]

    check_log_statements(filenames, args.tests, args.comments)
    separator()

    check_dead_code(filenames)
    separator()

    check_unwraps(filenames, args.tests, args.comments)
    separator()

    check_todo_items(filenames, args.tests)
    separator()

    # Cargo.toml files
    filenames = glob.glob("**/Cargo.toml", recursive=True)

    check_cargo_toml(filenames)
    separator()

# Vibe

A super awesome discord chat bot to filter chat.

## Configuration

Make sure to copy `sample-config.json` into a new file file called `config.json` and fill in the respective values.

### Rules

Create a new directory called `rules`, or you can copy `sample-rules` with it. Every text file in that directory will be read.

#### Format

At the start of each file it has to include on the first line a `TYPE: <type here>` line, and following a line that contains `---`. Blank lines will not be read, or lines starting with a `#`.

Valid types are: `FILTER_REGEX`, `FILTER_REGEX_LOWER`, `IGNORE`.

Example:
```
TYPE: IGNORE
Ok works that include a bad one. Case insensitive.
-----
penistone
# Are crapes bad? Maybe...
crape
```
# Vibe

A super awesome discord moderation bot to filter chat. The main goal is to make everything configurable just from `config.toml` and the `sample-rules` directory.

## Configuration

Make sure to copy `sample-config.toml` into a new file file called `config.toml` and fill in the respective values.

### Rules

Create a new directory called `rules`, or you can copy `sample-rules` with it. Every TOML file in that directory will be read.

To see how to configure the TOML files check out `sample-rules/filter.toml`
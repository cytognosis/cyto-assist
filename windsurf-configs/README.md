# Windsurf Configurations

This directory contains configuration files for the [Windsurf IDE](https://windsurf.ai).

## Setup

1.  Copy the `rules` directory to `.windsurf/`:
    ```bash
    mkdir -p .windsurf
    cp -r windsurf-configs/rules .windsurf/
    ```

2.  The `.cascade.js` file in the project root is automatically detected by Windsurf.

## Customization

You can edit the rules in `.windsurf/rules/` to match your specific project needs. Changes in this directory (`windsurf-configs`) are committed to version control to share with the team, while local changes in `.windsurf/` can be ignored if desired (though usually good to share).

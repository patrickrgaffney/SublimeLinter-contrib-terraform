SublimeLinter-contrib-terraform
================================

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) provides an interface to [Terraform `validate`](https://www.terraform.io/docs/commands/validate.html). It will be used with files that have the `.tf` syntax.

![screenshot](screenshot.png)

## Installation

SublimeLinter must be installed in order to use this plugin. 

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

Before installing this plugin, you must ensure that `terraform` is installed on your system. This plugin requires a **minimum version** of v0.12.x for `terraform`. All versions before that lack the ability to have the `validate` command return JSON output, which this plugin relies on.

In order for `terraform` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. The docs cover [troubleshooting PATH configuration](http://sublimelinter.readthedocs.io/en/latest/troubleshooting.html#finding-a-linter-executable).

## Settings

- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

Additional SublimeLinter-terraform settings:

- *none at this time*

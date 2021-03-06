import json
import logging

from SublimeLinter.lint import Linter, LintMatch

logger = logging.getLogger('SublimeLinter.plugin.terraform')


class Terraform(Linter):
    # The executable plus all arguments used to lint. The $file_path
    # will be set by super(), and will be the folder path of the file
    # currently in the active view. The "validate" command only operates
    # on directories (modules), so it's provided here to avoid the
    # command attempting to guess what directory we are at.
    cmd = ('terraform', 'validate', '--json', '${file_path}')

    # The validate command uses a one-based reporting
    # for line and column numbers.
    line_col_base = (1, 1)

    # A dict of defaults for the linter’s settings.
    defaults = {
        'selector': 'source.terraform'
    }

    # Turn off stdin. The validate command requires a directory.
    template_suffix = '-'

    def find_errors(self, output):
        """
        Override the find_errors() output so that we can parse the JSON
        output directly instead of using a multiline regex to walk
        through it.
        """
        try:
            data = json.loads(output)
        except Exception as e:
            logger.warning(e)
            self.notify_failure()

        # If there are no errors, return to stop iteration,
        # then yield to turn this function into a generator.
        if data["valid"]:
            return
            yield

        # Iterate through the errors, yielding LintMatchs.
        for issue in data['diagnostics']:
            line, col = 0, 0
            filename = self.context.get("file_name")
            message = "Error"
            severity = issue["severity"]

            # Catch the specific error for unsatisfied plugin
            # requirements. The "detail" key is rather long.
            # If a "detail" key was given, we also use that.
            if issue["summary"] == "Could not satisfy plugin requirements":
                message = issue['summary']
            elif "detail" in issue:
                message = '{summary}: {detail}'.format(
                    summary=issue['summary'].replace("\n", " "),
                    detail=issue['detail'].replace("\n", " "),
                )
            else:
                message = issue['summary'].replace("\n", " ")

            # If the error or warning occured on the entire file,
            # there won't be a "range" key, so we use the defaults.
            if "range" in issue:
                line = issue["range"]["start"]["line"] - self.line_col_base[0]
                col = issue["range"]["start"]["column"] - self.line_col_base[1]

                # Only the basename is provided in "filename".
                filename = issue["range"]["filename"]

            yield LintMatch(
              filename=filename,
              line=line,
              col=col,
              error_type=severity,
              message=message,
            )

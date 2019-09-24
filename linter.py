import json
import logging
import os

from SublimeLinter.lint import Linter, LintMatch

logger = logging.getLogger('SublimeLinter.plugin.terraform')


class Terraform(Linter):
    # The executable plus all arguments used to lint.
    cmd = ('terraform', 'validate', '--json')

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
        current_file = self.view.file_name()
        project_folder = self.view.window().folders()[0]

        # TODO: this could break -- need a better solution to
        # getting project folder path.
        project_path = os.path.commonprefix([project_folder, current_file])

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
            message = '{summary}: {detail}'.format(
              summary=issue['summary'],
              detail=issue['detail']
            )
            severity = issue["severity"]
            error = severity if severity == "error" else ""
            warning = severity if severity == "warning" else ""
            line = issue["range"]["start"]["line"] - self.line_col_base[0]
            col = issue["range"]["start"]["column"] - self.line_col_base[0]
            filename = issue["range"]["filename"]
            full_file_name = "{}/{}".format(project_path, filename)

            yield LintMatch(
              match=issue,
              filename=full_file_name,
              line=line,
              col=col,
              error=error,
              warning=warning,
              message=message
            )

import re
from SublimeLinter.lint import Linter, ERROR
from SublimeLinter.lint.linter import LintMatch
from os.path import basename
import json
import logging

logger = logging.getLogger('SublimeLinter.plugin.terraform')

# Compile the multi-line regular expression
# to pull the relvent bits from the JSON output.
OUTPUT_RE = re.compile(
	r'\"severity\":\s*'
	r'\"((?P<error>error)|(?P<warning>warning))\",\s*'
	r'\"summary\":\s*'
	r'\"(?P<message>.+\s*.+)\",\s*'
	r'\"range\".+\s*'
	r'\"filename\":\s*'
	r'\"(?P<filename>.+)\",\s*'
	r'\"start\":.+\s*'
	r'\"line\":\s*'
	r'(?P<line>\d+),\s*'
	r'\"column\":\s*'
	r'(?P<col>\d+)'
)

class Terraform(Linter):
		# The executable plus all arguments used to lint.
    cmd = ('terraform', 'validate', '--json')

    # Name of the linter.
    name = 'terraform'

    # Default error type (for when the regex can't parse one).
    default_type = ERROR

    # Regex will parse multiple lines to find error messages.
    multiline = True
    regex = OUTPUT_RE

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
    	print(output)
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
    		line = issue["range"]["start"]["line"]
    		col = issue["range"]["start"]["column"]
    		filename = issue["range"]["filename"]

    		lm = LintMatch(
    			match={message, error, warning, line, col, filename},
    			line=int(line),
    			col=int(col),
    			error=error,
    			warning=warning,
    			message=message
    		)
    		print(lm)
    		yield lm

   #  def split_match(self, match):
   #  	"""
   #  	Override to fix the "message" output and to determine if we
			# should lint this file.
   #  	"""
   #  	match, line, col, error, warning, message, near = (
   #  		super().split_match(match)
   #  	)

   #  	print({match, line, col, error, warning, message, near})

   #  	# matched_file = match.groupdict()['filename']
   #  	# linted_file = basename(self.filename)

   #  	# # If the current file being linted is not the file wherein
   #  	# # we matched on an error, we override the return to avoid
   #  	# # showing "ghost" errors in the wrong file.
   #  	# if matched_file != linted_file:
   #  	# 	return None, None, None, None, None, '', None

   #  	# new_msg = clean_up_message(message)

   #  	return match, line, col, error, warning, new_msg, near

# Terraform validate returns a summary and a detail. We include both
# in the named capture group "message". These are matched over two
# separate JSON keys, so the string sent to split_match() contains
# a lot of extra junk -- namely the "detail" key and some whitespace.
# def clean_up_message(msg):
# 	# Split the message on the end of the "message" key value.
# 	split_msg = msg.split('",')

# 	# The first match is the value from the "summary" key.
# 	summary = split_msg[0]

# 	# Remove the whitespace and "detail" key from the message.
# 	raw_detail = re.sub(r'\s*\"detail\":\s*\"', '', split_msg[1])

# 	# Un-escape all JSON-escape double-quotes.
# 	detail = raw_detail.replace('\\"', '"')

# 	return '{summary}: {detail}'.format(summary=summary, detail=detail)
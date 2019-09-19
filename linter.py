import re
from SublimeLinter.lint import Linter, ERROR
from os.path import basename

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

    def split_match(self, match):
    	"""
    	Override to fix the "message" output and to determine if we
			should lint this file.
    	"""
    	match, line, col, error, warning, message, near = (
    		super().split_match(match)
    	)

    	matched_file = match.groupdict()['filename']
    	linted_file = basename(self.filename)

    	# If the current file being linted is not the file wherein
    	# we matched on an error, we override the return to avoid
    	# showing "ghost" errors in the wrong file.
    	if matched_file != linted_file:
    		return None, None, None, None, None, '', None

    	new_msg = clean_up_message(message)

    	return match, line, col, error, warning, new_msg, near

# Terraform validate returns a summary and a detail. We include both
# in the named capture group "message". These are matched over two
# separate JSON keys, so the string sent to split_match() contains
# a lot of extra junk -- namely the "detail" key and some whitespace.
def clean_up_message(msg):
	# Split the message on the end of the "message" key value.
	split_msg = msg.split('",')

	# The first match is the value from the "summary" key.
	summary = split_msg[0]

	# Remove the whitespace and "detail" key from the message.
	raw_detail = re.sub(r'\s*\"detail\":\s*\"', '', split_msg[1])

	# Un-escape all JSON-escape double-quotes.
	detail = raw_detail.replace('\\"', '"')

	return '{summary}: {detail}'.format(summary=summary, detail=detail)
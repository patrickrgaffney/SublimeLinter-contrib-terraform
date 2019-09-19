import re
from SublimeLinter.lint import Linter

# Compile the multi-line regular expression
# to pull the relvent bits from the JSON output.
OUTPUT_RE = re.compile(
	r'\"severity\":\s*'
	r'\"((?P<error>error)|(?P<warning>warning))\",\s*'
	r'\"summary\":\s*'
	r'\"(?P<message>.+\s*.+)\",\s*'
	r'\"range\".+\s*'
	r'\"filename\":.+\s*'
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

    # Regex will parse multiple lines to find error messages.
    multiline = True

    regex = OUTPUT_RE

    # A dict of defaults for the linter’s settings.
    defaults = {
        'selector': 'source.terraform'
    }

    # Turn off stdin.
    # template_suffix = 'tf'

    def split_match(self, match):
    	"""Override to fix the "message" output."""
    	match, line, col, error, warning, message, near = (
    		super().split_match(match)
    	)

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
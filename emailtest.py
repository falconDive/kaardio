import re
def email():
    pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
    email = raw_input("enter the mail address::")
    match = re.search(pattern, email)

    if not match:
        print "not valid:::"
    else:
        print "valid email :::", match.group()

email()

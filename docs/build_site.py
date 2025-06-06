from voltpeek import commands

with open('./commands.html.template', 'r') as infile:
    template = infile.read()
    template += commands.__doc__
    with open('./commands.html', 'w') as outfile:
        outfile.write(template)
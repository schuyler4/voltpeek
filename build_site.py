from voltpeek import commands

with open('../schuyler4.github.io/index.html.template', 'r') as infile:
    template = infile.read()
    template += commands.__doc__
    with open('../schuyler4.github.io/index.html', 'w') as outfile:
        outfile.write(template)
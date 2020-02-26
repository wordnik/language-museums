"""A tool to parse the PDF version of 'Language Museums of the World'
downloaded from
https://www.nynorsk.no/wp-content/uploads/2020/02/814-20180314-Language-museums-OG.pdf

The PDF was processed using pdftotext (from the 'poppler' library) with the '-layout' 
option. The resultant 814-20180314-Language-museums-OG.txt was copied into this repository.

"""
import re
from pathlib import Path
from slugify import slugify
import json
import sys

# Museum pages seem to start with a new-page mark (\x0c)
# have a year, in parentheses, followed immediately by a ','
# and 
MUSEUM_PAGE_PATTERN = re.compile('^\x0c(.+?)\s+\((\d{4})\),.*')

EXAMPLE_JSON = {
    "name": "Grimmwelt",
    "last_updated":  "2015",
    "location": "Kassel, Germany",
    "url": "www.grimms.de/museum",
    "email": "grimmnet@t-online.de",
    "address":"Weinbergstraße 21, 34117 Kassel",
    "phone":"+49 561 598 61 910"
}

def paginator(fn):
    """Given a filename, open it, and yield pages from it, treating
    ^L (control-L) as the sign of a new page.
    """
    buffer = []
    with open(fn) as f:
        for line in f.readlines():
            if line.startswith('\x0c'): # ^L
                yield buffer
                buffer = []
            buffer.append(line)
    yield buffer

def write_museum_json(page,output_dir=Path("museums-json")):
    match = MUSEUM_PAGE_PATTERN.match(page[0])
    name = match.group(1)
    year = match.group(2)

    location = page[1].strip() # this doesn't quite work, sometimes there's a subhead.
    record = {
        'name': name,
        'last_updated': year,
        'location': location
    }
    fn = slugify(name,only_ascii=True) + '.json'
    of = output_dir / Path(fn)
    json.dump(record,of.open('w'),indent=2)

def main():
    script = Path(__file__) # textfile is expected adjacent to script
    txtfile = script.parent / '814-20180314-Language-museums-OG.txt' 

    if (len(sys.argv) > 1):
        output_dir = Path(sys.argv[1])
    else:
        output_dir = Path('museums-json/')

    output_dir.mkdir(parents=True,exist_ok=True)

    for page in paginator(txtfile):
        if MUSEUM_PAGE_PATTERN.match(page[0]):
            write_museum_json(page, output_dir=output_dir)

if __name__ == '__main__':
    main()


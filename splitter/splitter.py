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
MUSEUM_PAGE_PATTERN = re.compile('^\x0c(.+?)\s+\((\d{4})\),.*\D$')
URL_PATTERN = re.compile("^(https?://)?[a-z\.\-]+/?.*$")
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

    record = parse_museum_page(page)

    fn = slugify(record['name'],only_ascii=True) + '.json'
    of = output_dir / Path(fn)

    json.dump(record,of.open('w'),indent=2)

def museum_page_to_blocks(page):
    """Just split up the page based on blank lines. If a page has 4 or more blocks,
       we think we can parse it, but fewer is weird...
    """
    blocks = []
    buffer = []
    for line in page:
        line = line.rstrip()
        if len(line) == 0:
            if buffer:
                blocks.append(buffer)
                buffer = []
        else:
            buffer.append(line)
    blocks.append(buffer)
    return blocks

def parse_museum_page(page):
    "Given an array of lines in museum page format, break it up into known pieces"

    match = MUSEUM_PAGE_PATTERN.match(page[0])
    name = match.group(1)
    year = match.group(2)

    record = {
        'name': name,
        'last_updated': year,
    }

    blocks = museum_page_to_blocks(page)
    if len(blocks) < 4:
        print(f"[{name}] has {len(blocks)} blocks so record will be incomplete")
    else:
        name_loc = blocks[0]
        contact = blocks[1] # 2 is text desc, 3 is page number
        if len(name_loc) > 1:
            # the location is usually second but sometimes third, 
            # always seems to be last.
            record['location'] = name_loc[-1].strip() 
        else:
            print(f"no location for {record['name']}")

        
        if URL_PATTERN.match(contact[0]):
            record['url'] = contact[0]
            contact = contact[1:]
        else:
            print(f"[{name}] can't find URL in {contact[0]}")

        if '@' in contact[0]:
            record['email'] = contact[0]
            contact = contact[1:]
        else:
            print(f"[{name}] can't find email in {contact[0]}")

        try:
            if contact[-1].index('Phone ') == 0:
                record['phone'] = contact[-1][len('Phone '):]
                contact = contact[:-1]
        except:
            print(f"[{name}] can't find phone in {contact[-1]}")

        if contact:
            record['address'] = ' '.join(contact)

        dump = '\n'.join(line.strip() for line in contact)
        if len(record) != 7:
            print("------")
            print(f"[{name}] has {len(record)} fields")
            print(f"\n{dump}\n")


    return record


def is_museum_page(page):
    # don't get fooled by table of contents
    return MUSEUM_PAGE_PATTERN.match(page[0]) and page[0].strip()[-1].isalpha()

def main():
    script = Path(__file__) # textfile is expected adjacent to script
    txtfile = script.parent / '814-20180314-Language-museums-OG.txt' 

    if (len(sys.argv) > 1):
        output_dir = Path(sys.argv[1])
    else:
        output_dir = Path('museums-json/')

    output_dir.mkdir(parents=True,exist_ok=True)

    for page in filter(is_museum_page,paginator(txtfile)):
        write_museum_json(page, output_dir=output_dir)

if __name__ == '__main__':
    main()


import re
from pathlib import Path
from slugify import slugify
import json

# Museum pages seem to start with a new-page mark (\x0c)
# have a year, in parentheses, followed immediately by a ','
# and 
MUSEUM_PAGE_PATTERN = re.compile('^\x0c(.+?)\s+\((\d{4}\)),.*')

EXAMPLE_JSON = {
    "name": "Grimmwelt",
    "last_updated":  "2015",
    "location": "Kassel, Germany",
    "url": "www.grimms.de/museum",
    "email": "grimmnet@t-online.de",
    "address":"Weinbergstraße 21, 34117 Kassel",
    "phone":"+49 561 598 61 910",
    "description_de": "Die GRIMMWELT Kassel will das schöpferische Leben und Wirken der Brüder Grimm einem breiten Publikum zugänglich machen. Sie stellt dazu die lebendige Vermittlung von Sprache und Literatur in den Mittelpunkt. Das Publikum soll motiviert werden, sich Wissensinhalte aktiv zu erschließen und positive Lernerlebnisse zu sammeln. Die GRIMMWELT Kassel arbeitet mit hervorragenden Künstlern, mit Kunst- und Medienvermittlern sowie mit kulturellen und sozialen Einrichtungen zusammen. Neben wertvollen Originalen sorgen Ton und Film, multimediale und interaktive Angebote sowie die künstlerischen Installationen für anregende Erfahrungen. Die GRIMMWELT Kassel schlägt Brücken zwischen Kultur und Literatur in die Welt des Publikums. Die erlebnisorientierte Vermittlung lädt dazu ein, eigene Lösungswege und Ausdrucksmöglichkeiten zu finden, Trends und Veränderungen wahrzunehmen, Entwicklungen zu verstehen und einzuordnen. Die GRIMMWELT Kassel wurde am 4. September 2015 eröffnet. Die Nutzfläche ist ca. 4000 qm, die Ausstellungsfläche 1.600 qm, und die Gesamtkosten für Bau und Einrichtung belaufen sich auf etwa 20 Millionen Euro."
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
    name = match.groups(1)
    year = match.groups(2)

    record = {
        'name': name,
        'last_updated': year
    }
    fn = slugify(name) + '.json'
    of = output_dir / Path(fn)
    json.dump(record,of.open('w'))

def main():
    for page in paginator('814-20180314-Language-museums-OG.txt'):
        if MUSEUM_PAGE_PATTERN.match(page[0]):
            write_museum_json(page)

if __name__ == '__main__':
    main()
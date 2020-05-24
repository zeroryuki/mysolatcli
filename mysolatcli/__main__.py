import argparse
import sys
import pyjq
import json
from mysolatcli import SolatAPI
from yaspin import yaspin
from argparse import ArgumentParser
from tabulate import tabulate

api = None
sp = yaspin(text="Fetching Data..", color="green")

def init_api():
    global api
    api = SolatAPI()

def format_value(val):
    """
    A helper function to format fields for table output.
    Converts nested dicts into multilist strings.
    """
    if isinstance(val, dict):
        return "\n".join([ f"{k}: {val[k]}" for k in val.keys()])
    return val

def get_zon(lokasi):
    sp.start()
    zon = api.get_zones()
    zone = pyjq.all(".results[]|select(.lokasi == $lokasi)", zon, vars={"lokasi": lokasi})
    if zone == []:
       #print("Lokasi not in any zone. Please try with another location")
       sp.red.fail("✘")
       print("Lokasi not in any zone. Please try with another location")
       sys.exit()
    sp.ok()
    return zone[0]['zone']

def data_for_jadual(data,fields):
    data_format = list(map(lambda loc: [ format_value(loc[field]) for field in fields], data))
    return data_format

def jadual_lokasi(args):
    lok = get_zon(args.lokasi.title())
    if args.fields:
       fields = ["tarikh"] + args.fields or ["tarikh","subuh","zohor","asar","maghrib","isyak"]

    data = pyjq.all(".prayer_times[]|{tarikh:.date,subuh:.subuh,zohor:.zohor,asar:.asar,maghrib:.maghrib,isyak:.isyak}", api.get_week(lok)) if args.minggu else pyjq.one(".|[{tarikh:.prayer_times.date,subuh:.prayer_times.subuh,zohor:.prayer_times.zohor,asar:.prayer_times.asar, maghrib:.prayer_times.maghrib,isyak:.prayer_times.isyak}]", api.get_today(lok))

    data_format = data_for_jadual(data,fields)
    print(tabulate(data_format,fields,tablefmt="fancy_grid"))

def info_zon(args, fields=["zone","negeri","lokasi"]):

    def jadual_negeri(negeri):
        fetch_state = api.get_negeri(args.negeri) if args.negeri else api.get_negeri()

        states = pyjq.one(".states", fetch_state)
        myzone = []

        sp.start()
        for i in range(len(states)):
            fetch_zon = api.get_negeri(str(states[i]))
            data = pyjq.all(".results[]", fetch_zon)
            myzone.append(data)
            sp.hide()
            sp.write(states[i] + "✅")
        sp.ok()

        zon_formatted = pyjq.all(".[][]", myzone)
        data_format = data_for_jadual(zon_formatted,fields)
        print(tabulate(data_format,fields, tablefmt="fancy_grid"))

    if args.zonkod is None:
        jadual_negeri(args.negeri)
    else:
        sp.start()
        fetch_zon = api.get_today(args.zonkod)
        data = pyjq.one(".|{zone,tarikh:.prayer_times.date,locations,azan:{subuh:.prayer_times.subuh,zohor: .prayer_times.zohor, asar: .prayer_times.asar, maghrib:.prayer_times.maghrib, isyak:.prayer_times.isyak}}",fetch_zon)
        fields = data.keys()
        vals = list(map(lambda x: format_value(data[x]), fields))
        items = list(zip(fields, vals))
        sp.ok()
        print(tabulate(items, tablefmt="fancy_grid"))

def show_help(parser, command=None):
    args = []
    if command is not None:
        args = [command]
    if not "-h" in sys.argv and not "--help" in sys.argv:
        args.append('-h')
        print("\n")
        parser.parse_args(args) 

def parse_args():
    """
    Setup the argument parser. 
    The parser is setup to use subcommands so that each command can be extended in the future with its own arguments.
    """
    ArgumentParser()
    parser = ArgumentParser(
        prog="mysolatcli",
        description="Simple CLI tools for Malaysia Prayer Time"
        
    )
    parser.set_defaults(command=None)
    command_parsers = parser.add_subparsers(title="commands", prog="mysolatcli")

    jadual_parser = command_parsers.add_parser("jadual", help="Prayer time by location/state")
    jadual_parser.add_argument("-l","--lokasi", required=True, metavar="lokasi",  type=str, help="Show table based on location (Ex: gombak)")
    jadual_parser.add_argument("-m","--minggu", action="store_true", help="Print out prayer time for week")
    jadual_parser.add_argument("-f", "--fields", metavar="field", default=["subuh","zohor","asar","maghrib","isyak"], nargs="+", type=str, help="only print this value (Ex: zohor isyak)")
    jadual_parser.set_defaults(func=jadual_lokasi, command="jadual")

    zon_parser = command_parsers.add_parser("zon", help="Info for zones")
    zon_parser.add_argument("-n","--negeri", type=str, help="Show zone in the states")
    zon_parser.add_argument("-z","--zonkod", type=str, help="Print info for zone")
    zon_parser.set_defaults(func=info_zon, command="zon")

    try:
        args = parser.parse_args()
    except:
        subcommand=None
        if len(sys.argv) >= 2:
            subcommand = sys.argv[1]
            show_help(parser, subcommand)
        sys.exit(1)
    return args, parser

def main():
    args, parser = parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    init_api()
    args.func(args)

if __name__=="__main__":
    main()

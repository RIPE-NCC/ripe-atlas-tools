import json
import traceback
import urllib2

from .base import Command as BaseCommand


class Command(BaseCommand):

    help = "Create a new RIPE Atlas UDM."
    url_path = "/api/v1/measurement/?key=%s"
    post_data = {}

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.measurement_type = None
        self.msm_id = None
        self.tries = 2
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        """
        Holds different stuff that we should do in init but we'd rather keep
        __init__ clean.
        """
        key = self.get_api_key()
        if not key:
            print("You have to specify a valid API key.")
            return
        self.url = "%s%s" % (self.server, self.url_path % key)

    def get_api_key(self):
        """Gets API key either from a given file or by stdin."""
        if not self.parser_options.key_file:
            key = raw_input("Specify your API key: ")
            if not key:
                return False
        else:
            try:
                file_descriptor = open(self.parser_options.key_file)
                key = file_descriptor.read().strip()
            except:
                print(traceback.format_exc())
                print("Error while reading given API key file.")
                return False

        return key

    def run(self):
        """
        Main function that collects all users information from stdin, and
        creates a new UDM.
        """
        # if we have a file with ready post data skip reading from stdin and do
        # request.
        if self.parser_options.post_data_file:
            file_descriptor = open(self.parser_options.post_data_file, "r")
            self.post_data = json.loads(file_descriptor.read().strip())
        else:
            try:
                self.data_from_stdin()
                confirm_msg = (
                    "You are about to create a new RIPE Atlas UDM with the "
                    "following details:\n%s\n[y/n]:"
                ) % self.post_data
                if raw_input(confirm_msg) != "y":
                    print "Just exiting."
                    return False
            except KeyboardInterrupt:
                return False

        msm_id = self.create()
        if not msm_id:
            return False

        self.msm_id = msm_id
        print "A new UDM just created with id: %d" % msm_id

        return True

    def get_type(self):
        """Gets the type of the new measurement from user input."""
        msg = "Specify Type[ping/traceroute/dns/sslcert]:"
        for _ in range(self.tries):
            measurement_type = raw_input(msg).strip()
            if measurement_type in ("ping", "traceroute", "dns", "sslcert"):
                return measurement_type

        raise InvalidEntry("Invalid entry for measurement type.")

    def get_target(self):
        """Gets the target of the new measurement from user input."""
        msg = "Specify Target"
        warning_msg = ""
        for _ in range(self.tries):
            target = raw_input("%s:" % (msg + warning_msg)).strip()
            if target:
                return target
            elif target == "" and self.measurement_type == "dns":
                return target
            elif target == "":
                warning_msg = "(target should be an non empty string.)"

        raise InvalidEntry("Invalid entry for measurement target.")

    def get_type_protocol(self):
        """
        If type of measurement is traceroute then protocol should be added
        as well.
        """
        msg = 'Specify Traceroute Protocol[ICMP/UDP/TCP]:'
        for _ in range(self.tries):
            trace_protocol = raw_input(msg).strip()
            if trace_protocol in ("ICMP", "UDP", "TCP"):
                return trace_protocol

        raise InvalidEntry('Invalid entry for traceroute protocol.')

    def get_ip_version(self):
        """Gets the version of ip of the new measurement from user input."""
        msg = 'Specify Protocol[4/6]:'
        for _ in range(self.tries):
            addr_family = raw_input(msg).strip()
            if addr_family in ("4", "6"):
                return int(addr_family)

        raise InvalidEntry('Invalid entry for IP version.')

    def get_description(self):
        """Gets the description of the new measurement from user input."""
        msg = "Specify Description:"
        for _ in range(self.tries):
            description = raw_input(msg).strip()
            if description:
                return description

        raise InvalidEntry('Invalid entry for measurement description.')

    def get_is_oneoff(self):
        """Is new measurement ONEOFF."""
        mapping = {"y": True, "n": False}
        msg = "Is it OneOff [y/n]:"
        for _ in range(self.tries):
            is_oneoff = raw_input(msg).strip()
            if is_oneoff in ("y", "n"):
                return mapping[is_oneoff]

        raise InvalidEntry('Invalid entry for oneoff boolean.')

    def get_interval(self):
        """Gets the interval of the new measurement from user input."""
        msg = "Specify Interval[Leave blank for default]:"
        for _ in range(self.tries):
            interval = raw_input(msg).strip()
            if interval == "":
                return interval
            if interval.isdigit() and interval != '0':
                return int(interval)

        raise InvalidEntry('Invalid entry for measurement interval.')

    def get_additional_options(self):
        """
        Gets the additional options for the new measurement from user input.
        """
        additional_options = {}
        if raw_input('Do you need any additional options [y/n]:') == 'y':
            while True:
                option = raw_input('Specify option:')
                if not option:
                    break
                value = raw_input('Specify value:')
                additional_options[option] = value
                if raw_input('More [y/n]:') == 'y':
                    continue
                else:
                    break

        return additional_options

    def fill_definitions(self):
        """Fill definitions structure from user input."""

        definitions = {}
        self.measurement_type = definitions["type"] = self.get_type()
        definitions["target"] = self.get_target()
        if self.measurement_type == 'traceroute':
            definitions["protocol"] = self.get_type_protocol()
        definitions["af"] = self.get_ip_version()
        definitions["description"] = self.get_description()
        self.is_oneoff = definitions["is_oneoff"] = self.get_is_oneoff()
        if not self.is_oneoff:
            interval = self.get_interval()
            if interval:
                definitions["interval"] = interval
        additional_options = self.get_additional_options()
        if additional_options:
            definitions.update(additional_options)
        self.post_data['definitions'] = [definitions]

    def get_start_time(self):
        """Gets the start time for the new measurement from user input."""
        msg = "Specify Start Time [Unix Timestamp\Leave blank for now]:"
        for _ in range(self.tries):
            start_time = raw_input(msg).strip()
            if start_time == "":
                return start_time
            if start_time.isdigit() and start_time > "0":
                return int(start_time)

        raise InvalidEntry('Invalid entry for measurement start time.')

    def get_end_time(self):
        """Gets the end time for the new measurement from user input."""
        msg = "Specify End Time [Unix Timestamp\Leave blank for never]:"
        for _ in range(self.tries):
            end_time = raw_input(msg).strip()
            if end_time == "":
                return end_time
            if end_time.isdigit() and end_time > "0":
                return int(end_time)

        raise InvalidEntry('Invalid entry for measurement end time.')

    def fill_times(self):
        """Fill times from user input."""
        start_time = self.get_start_time()
        if start_time:
            self.post_data['start_time'] = start_time
        if not self.is_oneoff:
            end_time = self.get_end_time()
            if end_time:
                self.post_data['end_time'] = end_time

    def get_probes_number(self):
        """Get number of probes requested from user input."""
        msg = "Specify Number of Probes (Integer):"
        for _ in range(self.tries):
            probes_number = raw_input(msg).strip()
            if probes_number.isdigit() and probes_number > '0':
                return int(probes_number)

        raise InvalidEntry('Invalid entry for number of probes.')

    def get_probes_source_type(self):
        """Get the source of probes from user input."""
        msg = (
            "Specify Probes Source Type [area/country/prefix/asn/probes/msm]:"
        )
        accepted_sources = (
            "area", "country", "prefix", "asn", "probes", "msm"
        )
        for _ in range(self.tries):
            probe_source_type = raw_input(msg).strip()
            if probe_source_type in accepted_sources:
                return probe_source_type

        raise InvalidEntry("Invalid entry for probe's source.")

    def get_probes_source_value(self):
        """Get the value of source of probes from user input."""
        msg = "Specify Probes Source:"
        for _ in range(self.tries):
            probe_source = raw_input(msg).strip()
            if probe_source:
                return probe_source

        raise InvalidEntry("Invalid entry for value of probe's source.")

    def fill_probes(self):
        """Fill probes structure from user input."""
        probes = {}
        probes['requested'] = self.get_probes_number()
        probes['type'] = self.get_probes_source_type()
        probes['value'] = self.get_probes_source_value()
        self.post_data['probes'] = [probes]

    def data_from_stdin(self):
        '''
        Collects from stdin all information that a user most likely wants to
        specify.
        '''
        self.fill_definitions()
        self.fill_times()
        self.fill_probes()

    def create(self):
        '''
        Makes the http post that create the UDM itself.
        '''
        post_data = json.dumps(self.post_data)
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        try:
            response = urllib2.urlopen(req, post_data)
        except urllib2.HTTPError as exc:
            log = "HTTP ERROR %d: %s <%s>" % (exc.code, exc.msg, exc.read())
            print log
            return False

        response = json.load(response)
        if (
            'measurements' in response and
            isinstance(response['measurements'], list)
        ):
            return response['measurements'][0]
        else:
            print "HTTP output was not what we expected <%s>" % response
            return False


class InvalidEntry(Exception):
    pass

"""Python SDK providing access to Aignostics AI services."""

# TODO (Andreas): Fix CERTIFICATE_VERIFY_FAILED : unable to get local issuer certificate
# HACK START to workaround
import os
import ssl

import pip_system_certs.wrapt_requests  # noqa: F401

from .constants import MODULES_TO_INSTRUMENT
from .utils.boot import boot

myssl = ssl.create_default_context()
myssl.check_hostname = False
myssl.verify_mode = ssl.CERT_NONE
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["REQUESTS_CA_BUNDLE"] = ""

# HACK END


boot(modules_to_instrument=MODULES_TO_INSTRUMENT)

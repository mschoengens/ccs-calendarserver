##
# Copyright (c) 2006-2016 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

import re
from twisted.internet.defer import inlineCallbacks, returnValue
from twext.python.log import Logger
from twext.python.types import MappingProxyType
from twext.who.aggregate import DirectoryService as AggregateDirectoryService
from twext.who.idirectory import (
    FieldName as BaseFieldName, RecordType, DirectoryConfigurationError
)
from twext.who.util import ConstantsContainer
from twisted.cred.credentials import UsernamePassword
from twisted.python.filepath import FilePath
from twisted.python.reflect import namedClass
from twistedcaldav.config import fullServerPath
from txdav.who.augment import AugmentedDirectoryService
from txdav.who.cache import CachingDirectoryService
from txdav.who.delegates import DirectoryService as DelegateDirectoryService
from txdav.who.idirectory import (
    RecordType as CalRecordType,
    FieldName as CalFieldName
)
from txdav.who.wiki import DirectoryService as WikiDirectoryService
from txdav.who.xml import DirectoryService as XMLDirectoryService
from txdav.caldav.datastore.scheduling.ischedule.localservers import buildServersDB


log = Logger()


def directoryFromConfig(config, store):
    """
    Return a directory service based on the config.  If you want to go through
    AMP to talk to one of these as a client, instantiate
    txdav.dps.client.DirectoryService
    """

    # Note: Currently the directory needs a store, and the store needs a
    # directory.  Originally the directory's store was going to be different
    # from the calendar and contacts store, but we're not doing that, maybe
    # ever, since it brings more headaches (managing multiple schema upgrades,
    # etc.) You can pass store=None in here and the store will be created for
    # you, but don't pass store=None if you already have called storeFromConfig()
    # within this same process; pass that store in instead.

    # TODO: use proxyForInterface to ensure we're only using the DPS related
    # store API.  Also define an IDirectoryProxyStore Interface
    assert store is not None

    serversDB = buildServersDB(config.Servers.MaxClients) if config.Servers.Enabled else None

    return buildDirectory(
        store,
        config.DataRoot,
        [config.DirectoryService, config.ResourceService],
        config.AugmentService,
        config.Authentication.Wiki,
        serversDB=serversDB,
        cachingSeconds=config.DirectoryProxy.InSidecarCachingSeconds,
        filterStartsWith=config.DirectoryFilterStartsWith
    )


def buildDirectory(
    store, dataRoot, servicesInfo, augmentServiceInfo, wikiServiceInfo,
    serversDB=None, cachingSeconds=0, filterStartsWith=False
):
    """
    Return a directory without using a config object; suitable for tests
    which need to have mulitple directory instances.

    @param store: The store.
    @param dataRoot: The path to the directory containing xml files for any xml
        based services.
    @param servicesInfo:  An interable of ConfigDicts mirroring the
        DirectoryService and ResourceService sections of stdconfig
    @param augmentServiceInfo: A ConfigDict mirroring the AugmentService section
        of stdconfig
    @param wikiServiceInfo: A ConfigDict mirroring the Wiki section of stdconfig
    @param serversDB: A ServersDB object to assign to the directory
    """

    aggregatedServices = []
    cachingServices = []
    ldapService = None  # LDAP DS has extra stats (see augment.py)

    for serviceValue in servicesInfo:

        if not serviceValue.Enabled:
            continue

        directoryType = serviceValue.type.lower()
        params = serviceValue.params

        if "xml" in directoryType:
            xmlFile = params.xmlFile
            xmlFile = fullServerPath(dataRoot, xmlFile)
            fp = FilePath(xmlFile)
            if not fp.exists():
                fp.setContent(DEFAULT_XML_CONTENT)
            directory = XMLDirectoryService(fp)

        elif "opendirectory" in directoryType:
            from txdav.who.opendirectory import (
                DirectoryService as ODDirectoryService
            )
            # We don't want system accounts returned in lookups, so tell
            # the service to suppress them.
            node = params.node
            directory = ODDirectoryService(nodeName=node, suppressSystemRecords=True)

        elif "ldap" in directoryType:
            from twext.who.ldap import (
                DirectoryService as LDAPDirectoryService,
                FieldName as LDAPFieldName,
                RecordTypeSchema
            )

            if params.credentials.dn and params.credentials.password:
                creds = UsernamePassword(
                    params.credentials.dn,
                    params.credentials.password
                )
            else:
                creds = None
            mapping = params.mapping
            extraFilters = params.extraFilters
            directory = LDAPDirectoryService(
                params.uri,
                params.rdnSchema.base,
                useTLS=params.useTLS,
                credentials=creds,
                fieldNameToAttributesMap=MappingProxyType({
                    BaseFieldName.uid: mapping.uid,
                    BaseFieldName.guid: mapping.guid,
                    BaseFieldName.shortNames: mapping.shortNames,
                    BaseFieldName.fullNames: mapping.fullNames,
                    BaseFieldName.emailAddresses: mapping.emailAddresses,
                    LDAPFieldName.memberDNs: mapping.memberDNs,
                    CalFieldName.readOnlyProxy: mapping.readOnlyProxy,
                    CalFieldName.readWriteProxy: mapping.readWriteProxy,
                    CalFieldName.loginAllowed: mapping.loginAllowed,
                    CalFieldName.hasCalendars: mapping.hasCalendars,
                    CalFieldName.autoScheduleMode: mapping.autoScheduleMode,
                    CalFieldName.autoAcceptGroup: mapping.autoAcceptGroup,
                    CalFieldName.serviceNodeUID: mapping.serviceNodeUID,
                }),
                recordTypeSchemas=MappingProxyType({
                    RecordType.user: RecordTypeSchema(
                        relativeDN=params.rdnSchema.users,
                        attributes=(),
                    ),
                    RecordType.group: RecordTypeSchema(
                        relativeDN=params.rdnSchema.groups,
                        attributes=(),
                    ),
                    CalRecordType.location: RecordTypeSchema(
                        relativeDN=params.rdnSchema.locations,
                        attributes=(),
                    ),
                    CalRecordType.resource: RecordTypeSchema(
                        relativeDN=params.rdnSchema.resources,
                        attributes=(),
                    ),
                    CalRecordType.address: RecordTypeSchema(
                        relativeDN=params.rdnSchema.addresses,
                        attributes=(),
                    ),
                }),
                extraFilters={
                    RecordType.user: extraFilters.get("users", ""),
                    RecordType.group: extraFilters.get("groups", ""),
                    CalRecordType.location: extraFilters.get("locations", ""),
                    CalRecordType.resource: extraFilters.get("resources", ""),
                    CalRecordType.address: extraFilters.get("addresses", ""),
                },
                threadPoolMax=params.get("threadPoolMax", 10),
                authConnectionMax=params.get("authConnectionMax", 5),
                queryConnectionMax=params.get("queryConnectionMax", 5),
                tries=params.get("tries", 3),
                warningThresholdSeconds=params.get("warningThresholdSeconds", 5),
            )
            ldapService = directory

        elif "inmemory" in directoryType:
            from txdav.who.test.support import CalendarInMemoryDirectoryService
            directory = CalendarInMemoryDirectoryService()

        else:
            log.error("Invalid DirectoryType: {dt}", dt=directoryType)
            raise DirectoryConfigurationError

        # Set the appropriate record types on each service
        types = []
        fieldNames = []
        for recordTypeName in params.recordTypes:
            recordType = {
                "users": RecordType.user,
                "groups": RecordType.group,
                "locations": CalRecordType.location,
                "resources": CalRecordType.resource,
                "addresses": CalRecordType.address,
            }.get(recordTypeName, None)

            if recordType is None:
                log.error("Invalid Record Type: {rt}", rt=recordTypeName)
                raise DirectoryConfigurationError

            if recordType in types:
                log.error("Duplicate Record Type: {rt}", rt=recordTypeName)
                raise DirectoryConfigurationError

            types.append(recordType)

        directory.recordType = ConstantsContainer(types)
        directory.fieldName = ConstantsContainer(
            (directory.fieldName, CalFieldName)
        )
        fieldNames.append(directory.fieldName)

        if cachingSeconds:
            directory = CachingDirectoryService(
                directory,
                expireSeconds=cachingSeconds
            )
            cachingServices.append(directory)

        aggregatedServices.append(directory)

    #
    # Setup the Augment Service
    #
    serviceClass = {
        "xml": "twistedcaldav.directory.augment.AugmentXMLDB",
    }

    for augmentFile in augmentServiceInfo.params.xmlFiles:
        augmentFile = fullServerPath(dataRoot, augmentFile)
        augmentFilePath = FilePath(augmentFile)
        if not augmentFilePath.exists():
            augmentFilePath.setContent(DEFAULT_AUGMENT_CONTENT)

    augmentClass = namedClass(serviceClass[augmentServiceInfo.type])
    log.info(
        "Configuring augment service of type: {augmentClass}",
        augmentClass=augmentClass
    )
    try:
        augmentService = augmentClass(**augmentServiceInfo.params)
    except IOError:
        log.error("Could not start augment service")
        raise

    userDirectory = None
    for directory in aggregatedServices:
        if RecordType.user in directory.recordTypes():
            userDirectory = directory
            break
    else:
        log.error("No directory service set up for users")
        raise DirectoryConfigurationError

    # Delegate service
    delegateDirectory = DelegateDirectoryService(
        userDirectory.realmName,
        store
    )
    # (put at front of list so we don't try to ask the actual DS services
    # about the delegate-related principals, for performance)
    aggregatedServices.insert(0, delegateDirectory)

    # Wiki service
    if wikiServiceInfo.Enabled:
        aggregatedServices.append(
            WikiDirectoryService(
                userDirectory.realmName,
                wikiServiceInfo.EndpointDescriptor,
            )
        )

    # Aggregate service
    aggregateDirectory = AggregateDirectoryService(
        userDirectory.realmName, aggregatedServices
    )

    # Augment service
    try:
        fieldNames.append(CalFieldName)
        augmented = AugmentedDirectoryService(
            aggregateDirectory, store, augmentService
        )
        augmented.fieldName = ConstantsContainer(fieldNames)

        # The delegate directory needs a way to look up user/group records
        # so hand it a reference to the augmented directory.
        # FIXME: is there a better pattern to use here?
        delegateDirectory.setMasterDirectory(augmented)

        # Tell each caching service what method to use when reporting
        # times and cache stats
        for cachingService in cachingServices:
            cachingService.setTimingMethod(augmented._addTiming)

        # LDAP has additional stats to report
        augmented._ldapDS = ldapService

    except Exception as e:
        log.error("Could not create directory service", error=e)
        raise

    if serversDB is not None:
        augmented.setServersDB(serversDB)

    if filterStartsWith:
        augmented.setFilter(startswithFilter)

    return augmented


DEFAULT_XML_CONTENT = """<?xml version="1.0" encoding="utf-8"?>

<directory realm="Realm"/>
"""

DEFAULT_AUGMENT_CONTENT = """<?xml version="1.0" encoding="utf-8"?>

<augments/>
"""


@inlineCallbacks
def startswithFilter(
    method, tokens, expression, recordTypes=None, records=None,
    limitResults=None, timeoutSeconds=None
):
    """
    Call the passed-in method to retrieve records from the directory, but
    further filter the results by only returning records whose email addresses
    and names actually start with the tokens.  Without this filter, it's only
    required that the record's fullname *contains* the tokens. "Names" are split
    from the record's fullname, delimited by whitespace and hypens.
    """

    tokens = [t.lower() for t in tokens]

    results = []
    records = yield method(
        expression, recordTypes=recordTypes, limitResults=1000,
        timeoutSeconds=timeoutSeconds
    )
    count = 0
    for record in records:
        try:
            names = list(record.emailAddresses)
        except AttributeError:
            names = []
        for fullName in record.fullNames:
            names.extend(re.split(' |-', fullName))
        match = True  # assume it will match
        for token in tokens:
            for name in names:
                if name.lower().startswith(token):
                    break
            else:
                # there was no match for this token
                match = False
                break
        if match:
            results.append(record)
            count += 1
            if limitResults and count == limitResults:
                break

    returnValue(results)

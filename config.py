# The default PyroScope configuration script
#
# For details, see http://code.google.com/p/pyroscope/wiki/UserConfiguration
#

def _custom_fields():
    """ Yield custom field definitions.
    """
    import os
    from pyrocore.torrent import engine, matching
    from pyrocore.util import fmt

    yield engine.DynamicField(int,"uploaded_last_day","bytes uploaded in the last day",
        matcher=matching.ByteSizeFilter, accessor=lambda o: get_custom_uploaded_last(o,'day'))
    
    yield engine.DynamicField(int,"uploaded_last_week","bytes uploaded in the last week",
        matcher=matching.ByteSizeFilter, accessor=lambda o: get_custom_uploaded_last(o,'week'))

    yield engine.DynamicField(int,"uploaded_last_month","bytes uploaded in the last month",
        matcher=matching.ByteSizeFilter, accessor=lambda o: get_custom_uploaded_last(o,'month'))

    
    # PUT CUSTOM FIELD CODE HERE

def _get_custom_uploaded_last(obj,timelength):
    "Get an aggregated custom upload value field"
    try:
        result = int(obj._engine._rpc.d.get_custom(obj._fields["hash"],'uploaded_last_'+timelength))
    except ValueError as e:
        result = int(0) # values doesn't exist yet, probably a new torrent.
    return result
# Register our factory with the system
custom_field_factories.append(_custom_fields)

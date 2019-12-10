# convert internal trace dataset names to human readable ones for visualization
human_readable = {
    'openstack': 'OpenStack',
    'xtrace': 'XTrace'
}



# return the requests for each dataset
request_types_per_dataset = {
    'openstack': ['ServerCreate', 'ServerDelete', 'ServerList'],
    'xtrace': ['get', 'ls', 'put', 'rm']
}

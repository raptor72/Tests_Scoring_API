import pytest
from collections import namedtuple

def inc(x):
    return x + 1

def test_answer():
#    assert inc(3) == 5
    assert inc(7) == 8

def test_answer2():
    assert inc(3) == 4

class TestSomeThing:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
#        assert hasattr(x, "check")
        assert hasattr(x, "replace")
        print(dir(x))

def testNeedFiles(tmpdir):
    print(tmpdir)
#    assert 0

@pytest.fixture
def redis_connection():
    import redis
    r = redis.Redis()
    return r

def test_redis_info(redis_connection):
    info = redis_connection.info()
    assert info['redis_version'] == '3.2.12'
#    assert 0

Lastlog = namedtuple('Lastlog', ['mtime', 'path', 'name', 'extension', 'additions', 'bulvalue'])
Lastlog.__new__.__defaults__ = ('1970.01.01 00:00:00', '/', 'test', '.sh', None, False)

@pytest.fixture
def load_lastlog():
    Lastlog = namedtuple('Lastlog', ['mtime', 'path', 'name', 'extension', 'additions', 'bulvalue'])
    Lastlog.__new__.__defaults__ = ('1970.01.01 00:00:00', '/', 'test', '.sh', None, False)
    return Lastlog

def test_default_namedtuple():
    l1 = Lastlog()
    l2 = Lastlog('1970.01.01 00:00:00', '/', 'test', '.sh', None, False)
    assert l1 == l2

def test_default_namedtuple_fixture(load_lastlog):
    l1 = load_lastlog()
    l2 = load_lastlog('1970.01.01 00:00:00', '/', 'test', '.sh', None, False)
    assert l1 == l2

def test_lastlog_fields():
    l = Lastlog('2000.01.01 00:00:00', '/root')
#    print(l)
    assert l.mtime > '1970.01.01 00:00:00'
    assert l.mtime == '2000.01.01 00:00:00'
    assert l.path == '/root'
    assert (l.additions, l.bulvalue) == (None, False)

def test_lastlog_fields_fixture(load_lastlog):
    l = load_lastlog('2000.01.01 00:00:00', '/root')
#    print(l)
    assert l.mtime > '1970.01.01 00:00:00'
    assert l.mtime == '2000.01.01 00:00:00'
    assert l.path == '/root'
    assert (l.additions, l.bulvalue) == (None, False)

def test_lastlog_asdict():
    l_task = Lastlog('2000.01.01 00:00:00', '/root', 'Test', '.py', None, True)
    l_dict = l_task._asdict()
#    print('l_dist is: ', l_dict)
    expected = {'mtime': '2000.01.01 00:00:00',
                'path': '/root',
                'name': 'Test',
                'extension': '.py',
                'additions': None,
                'bulvalue': True}
    assert l_dict == expected

def test_lastlog_asdict_fixture(load_lastlog):
    l_task = load_lastlog('2000.01.01 00:00:00', '/root', 'Test', '.py', None, True)
    l_dict = l_task._asdict()
#    print('l_dist is: ', l_dict)
    expected = {'mtime': '2000.01.01 00:00:00',
                'path': '/root',
                'name': 'Test',
                'extension': '.py',
                'additions': None,
                'bulvalue': True}
    assert l_dict == expected


@pytest.fixture
def load_yaml_data():
    import yaml
    with open('sample.yml', 'r') as descriptor:
        try:
            load = yaml.safe_load(descriptor)
#            print(load)
#            print(type(load))
        except yaml.YAMLError as e:
            print(e)
    return load

def test_yaml_data(load_yaml_data):
    assert len(load_yaml_data) > 0
    assert 'dslVersion' in load_yaml_data['properties']

@pytest.fixture
def get_dict_from_yaml(load_yaml_data):
    queues = {}
    for components_name, settings in load_yaml_data['components'].items():
        queues.update({settings['properties']['name']: {}})
        for qparam, qvalue in load_yaml_data['components'][components_name]['properties'].items():
            queues[settings['properties']['name']].update({qparam: qvalue})
#    print(queues)
    return queues

def test_component_data(get_dict_from_yaml):
    for component in get_dict_from_yaml.keys():
#        print(get_dict_from_yaml[component])
        assert get_dict_from_yaml[component]['type'] is not None
        assert len(get_dict_from_yaml[component]['type']) > 0
        with pytest.raises(Exception) as e:
            get_dict_from_yaml[component]['typr']
        assert 'KeyError' in str(e)
#        print(e)
    assert len(get_dict_from_yaml) > 0



def test_recursion_depth():
    with pytest.raises(RuntimeError) as execinfo:
        def f():
            f()
        f()
#    print(execinfo)
    assert "maximum recursion" in str(execinfo.value)


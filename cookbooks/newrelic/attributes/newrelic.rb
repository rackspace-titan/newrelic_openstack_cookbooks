#default[:newrelic][:license_key] = "ABCDEFG...."
#
default[:newrelic][:log_level] = "info"
default[:newrelic][:pidfile] = "/var/run/newrelic-daemon.pid"
default[:newrelic][:logfile] = "/var/log/newrelic/newrelic-daemon.log"
default[:newrelic][:collector_host] = "collector.newrelic.com"
default[:newrelic][:ssl] = "false"
default[:newrelic][:timeout] = "30"
default[:newrelic][:socket] = "/tmp/.newrelic.sock"
default[:newrelic][:max_threads] = "8"
default[:newrelic][:metric_limit] = "2000"
default[:newrelic][:special] = "0"
default[:newrelic][:proxy] = ""

default[:newrelic][:tarball_url] = "http://dl.dropbox.com/u/22571016/newrelic-python-0.3.0.0-x86_64-unknown-linux-gnu.tar.gz"

# Nova API Configs
default[:newrelic][:nova_api_ini_path] = "/etc/newrelic/nova-api.ini"

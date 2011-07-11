#
# Cookbook Name:: newrelic
# Recipe:: install
#
# Copyright 2011, Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


directory "/etc/newrelic" do
  owner "root"
  group "root"
  mode "0700"
  action :create
end

template "/etc/newrelic/newrelic.cfg" do
  source "newrelic.cfg.erb"
  owner "root"
  group "root"
  mode 0600
end

remote_file "/tmp/newrelic.tar.gz" do
  source node[:newrelic][:tarball_url]
  mode "0644"
  action :nothing
  subscribes :create, resources("template[/etc/newrelic/newrelic.cfg]"), :immediately
end

bash "install newrelic" do
  action :nothing
  user "root"
  code <<-EOH
  INSTALL_TMP=$(mktemp -d) && cd $INSTALL_TMP
  tar xzf /tmp/newrelic.tar.gz
  cd newrelic-python*
  sh install.sh install
  python setup.py install
  rm /tmp/newrelic.tar.gz
  EOH
  subscribes :run, resources("remote_file[/tmp/newrelic.tar.gz]"), :immediately
end

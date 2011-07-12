# Cookbook Name:: newrelic
# Recipe:: nova-api
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

include_recipe "#{@cookbook_name}::install"

api_ini_path=node[:newrelic][:nova_api_ini_path]
api_instrumentation_path=node[:newrelic][:nova_api_instrumentation_path]
newrelic_config_dir=node[:newrelic][:newrelic_config_dir]
newrelic_log_dir=node[:newrelic][:newrelic_log_dir]

cookbook_file api_ini_path do
  source "nova-api.ini"
  mode "0644"
end

cookbook_file api_instrumentation_path do
  source "nova-api-instrumentation.py"
  mode "0644"
end

directory newrelic_config_dir do
  mode "755"
  action :create
end

directory newrelic_log_dir do
  mode "777"
  owner "nova"
  action :create
end

bash "inject_newrelic_nova_api" do
  user "root"
  code <<-EOH
  echo "#!/usr/bin/python" > /usr/bin/nova-api-new
  echo "import newrelic.agent" >> /usr/bin/nova-api-new
  echo "newrelic.agent.initialize('#{api_ini_path}')" >> /usr/bin/nova-api-new
  cat /usr/bin/nova-api >> /usr/bin/nova-api-new
  mv /usr/bin/nova-api-new /usr/bin/nova-api
  chmod 755 /usr/bin/nova-api
  EOH
  not_if "grep newrelic /usr/bin/nova-api"
end

service "nova-api" do
  restart_command "restart nova-api"
  subscribes :restart, resources("bash[inject_newrelic_nova_api]"), :immediately
end

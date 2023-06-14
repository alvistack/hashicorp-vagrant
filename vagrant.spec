# Copyright 2023 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
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

%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: vagrant
Epoch: 100
Version: 2.3.7
Release: 1%{?dist}
Summary: Build and distribute virtualized development environments
License: MIT
URL: https://github.com/hashicorp/vagrant/tags
Source0: %{name}_%{version}.orig.tar.gz
Source99: %{name}.rpmlintrc
BuildRequires: chrpath
BuildRequires: fdupes
BuildRequires: glibc-static
BuildRequires: golang-1.20
BuildRequires: libffi-devel
BuildRequires: ruby-devel >= 3.0
BuildRequires: rubygem(bundler)
Requires: ruby >= 3.0
Requires: rubygem(bundler)

%description
Vagrant is a tool for building and distributing virtualized development
environments.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
mkdir -p bin
set -ex && \
    export CGO_ENABLED=0 && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w -extldflags '-static -lm'" \
        -o ./bin/vagrant-go ./cmd/vagrant
bundle config set --local without development
bundle config set --local path ./bundle
bundle install --verbose --local --standalone
bundle config set --local deployment true
bundle install --verbose --local --standalone

%install
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm755 -d %{buildroot}%{_prefix}/share/bash-completion/completions
install -Dpm755 -d %{buildroot}/opt
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/vagrant-go
install -Dpm644 contrib/bash/completion.sh %{buildroot}%{_prefix}/share/bash-completion/completions/vagrant
mkdir -p %{buildroot}/opt/vagrant
tar xf ./vendor/cache/vagrant-2.3.7.gem data.tar.gz -O | tar zx -C %{buildroot}/opt/vagrant
cp -rfp .bundle bundle Gemfile.lock %{buildroot}/opt/vagrant/
pushd %{buildroot}/opt/vagrant && \
    bundle binstubs --all --force --path binstubs && \
    bundle exec vagrant --version && \
popd
ln -fs /opt/vagrant/binstubs/vagrant %{buildroot}%{_bindir}/vagrant
fdupes -qnrps %{buildroot}
find %{buildroot} -type f -name '*.so' -exec chrpath -d {} \;
find %{buildroot} -type f -exec sed -i 's?%{buildroot}??g' {} \;
find %{buildroot} -type f -exec sed -i 's?^#!.*ruby.*?#!/usr/bin/ruby?g' {} \;

%check

%files
%license LICENSE
%{_bindir}/*
%{_prefix}/share/bash-completion/completions/*
/opt/vagrant

%changelog

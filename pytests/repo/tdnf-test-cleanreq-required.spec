#
# tdnf-test-one spec file
#
Summary:    basic install test file.
Name:       tdnf-test-cleanreq-required
Version:    1.0.1
Release:    3
Vendor:     VMware, Inc.
Distribution:   Photon
License:    VMware
Url:        http://www.vmware.com
Group:      Applications/tdnftest

%description
Part of tdnf test spec. Basic install/remove/upgrade test

%prep

%build

%install
mkdir -p %{buildroot}/lib/cleanreq/
touch %{buildroot}/lib/cleanreq/required

%files
/lib/cleanreq/required

%changelog
*   Thu Nov 04 2021 Oliver Kurth <okurth@vmware.com> 1.0.1-1
-   clean req test

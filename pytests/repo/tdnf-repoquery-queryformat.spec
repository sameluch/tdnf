Summary:    Repoquery Test
Name:       tdnf-repoquery-queryformat
Version:    1.0.1
Release:    2
Vendor:     VMware, Inc.
Distribution:   Photon
License:    VMware
Url:        http://www.vmware.com
Group:      Applications/tdnftest
Requires:   tdnf-test-cleanreq1-required
Conflicts:  tdnf-test-conflicts-0
Provides:   tdnf-repoquery-queryformat
Obsoletes:  tdnf-test-obsoleted

%description
Part of tdnf test spec. For repoquery tests, other packages will
depend on this in some way.

%prep

%build

%install
mkdir -p %{buildroot}/usr/lib/repoquery
touch %{buildroot}/usr/lib/repoquery/%name

%files
/usr/lib/repoquery/%name

%changelog
*   Tue Jul 06 2021 Oliver Kurth <okurth@vmware.com> 1.0.1-2
-   first repoquery version

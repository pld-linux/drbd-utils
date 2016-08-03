# TODO:
# - working systemd service file

Summary:	Setup tools and scripts for DRBD
Summary(pl.UTF-8):	Narzędzie konfiguracyjne i skrypty dla DRBD
Summary(pt_BR.UTF-8):	Utilitários para gerenciar dispositivos DRBD
Name:		drbd-utils
Version:	8.9.7
Release:	0.2
License:	GPL v2+
Group:		Applications/System
Source0:	http://www.drbd.org/download/drbd/utils/%{name}-%{version}.tar.gz
# Source0-md5:	f2216346f8e77f352fb306ab357a8484
URL:		http://www.drbd.org/
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	udev-core
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(postun):	/usr/sbin/groupdel
Requires:	udev-core
Provides:	group(haclient)
Obsoletes:  drbdsetup
Obsoletes:	drbdsetup8
Obsoletes:	drbd-udev
Conflicts:  drbdsetup
Conflicts:	drbdsetup24
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Setup tool and init scripts for DRBD.

%description -l pl.UTF-8
Narzędzie konfiguracyjne i skrypty startowe dla DRBD.

%package -n resource-agents-drbd
Summary:	DRBD resource agents for a cluster setup
Group:		Daemons
Requires:	resource-agents

%description -n resource-agents-drbd
DRBD resource agents for a cluster setup.

%package -n bash-completion-drbd-utils
Summary:	bash-completion for drbd
Summary(pl.UTF-8):	Bashowe uzupełnianie poleceń dla drbd
Group:		Applications/Shells
Requires:	bash-completion
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-drbd-utils
This package provides bash-completion for drbd.

%description -n bash-completion-drbd-utils -l pl.UTF-8
Ten pakiet dostarcza bashowe uzupełnianie poleceń dla drbd.

%package -n drbd-xen
Summary:	Xen block device management script for DRBD
Group:		Applications/System
Requires:	drbdsetup = %{version}-%{release}
Requires:	xen

%description -n drbd-xen
This package contains a Xen block device helper script for DRBD,
capable of promoting and demoting DRBD resources as necessary.

%prep
%setup -q

%build
%configure \
	--with-initdir=/etc/rc.d/init.d \
    --with-udev \
    --with-xen \
    --with-pacemaker \
    --with-bashcompletion

%{__make} tools \
	KVER=dummy \
	CC="%{__cc}" \
	OPTCFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/sbin,%{_mandir}/man{5,8},%{_sysconfdir}} \
	$RPM_BUILD_ROOT/etc/ha.d/resource.d \
	$RPM_BUILD_ROOT/var/lib/drbd

%{__make} install \
	DRBD_ENABLE_UDEV=1 \
	DESTDIR=$RPM_BUILD_ROOT

#TODO
rm -rf $RPM_BUILD_ROOT/usr/share/man

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 60 haclient

%postun
if [ "$1" = "0" ]; then
	%groupremove haclient
fi

%files
%defattr(644,root,root,755)
/sbin/*
%attr(755,root,root) /usr/sbin/drbdadm
%attr(4754,root,haclient) /usr/sbin/drbdsetup
%attr(4754,root,haclient) /usr/sbin/drbdmeta
%dir %{_sysconfdir}/drbd.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/drbd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/drbd.d/global_common.conf
#%{_mandir}/man[58]/*
/lib/udev/rules.d/65-drbd.rules
%dir /lib/drbd
%attr(755,root,root) /lib/drbd/*
/usr/lib/tmpfiles.d/drbd.conf
%dir /usr/lib/drbd
%attr(755,root,root) /usr/lib/drbd/*
%attr(755,root,root) %{_sbindir}/drbd-overview
%attr(750,root,root) %dir /var/lib/drbd

%files -n resource-agents-drbd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/drbddisk
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/drbdupper
%dir /usr/lib/ocf/resource.d/linbit
%attr(755,root,root) /usr/lib/ocf/resource.d/linbit/*

%files -n bash-completion-drbd-utils
%defattr(644,root,root,755)
/etc/bash_completion.d/drbdadm

%files -n drbd-xen
%defattr(644,root,root,755)
/etc/xen/scripts/block-drbd

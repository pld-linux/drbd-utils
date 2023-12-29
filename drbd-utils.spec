Summary:	Setup tools and scripts for DRBD
Summary(pl.UTF-8):	Narzędzie konfiguracyjne i skrypty dla DRBD
Summary(pt_BR.UTF-8):	Utilitários para gerenciar dispositivos DRBD
Name:		drbd-utils
Version:	9.27.0
Release:	1
License:	GPL v2+
Group:		Applications/System
#Source0Download: https://linbit.com/linbit-software-download-page-for-linstor-and-drbd-linux-driver/
Source0:	https://pkg.linbit.com/downloads/drbd/utils/%{name}-%{version}.tar.gz
# Source0-md5:	d440bd8b9639b0e27f592ab598206273
Patch0:		%{name}-udev.patch
URL:		http://www.drbd.org/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext-tools
BuildRequires:	keyutils-devel
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	libxslt-progs
BuildRequires:	pkgconfig
BuildRequires:	po4a
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.671
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(postun):	/usr/sbin/groupdel
Requires:	udev-core >= 85
Provides:	group(haclient)
Obsoletes:	drbd-udev < 8.4.3
Obsoletes:	drbdsetup < 9
Obsoletes:	drbdsetup8 < 9
Conflicts:	drbdsetup
Conflicts:	drbdsetup24
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Setup tool and init scripts for DRBD.

%description -l pl.UTF-8
Narzędzie konfiguracyjne i skrypty startowe dla DRBD.

%package -n resource-agents-drbd
Summary:	DRBD resource agents for a cluster setup
Summary(pl.UTF-8):	Agenci zasobów DRBD do instalacji klastrowych
Group:		Daemons
Requires:	drbd-utils = %{version}-%{release}
Requires:	resource-agents

%description -n resource-agents-drbd
DRBD resource agents for a cluster setup.

%description -n resource-agents-drbd -l pl.UTF-8
Agenci zasobów DRBD do instalacji klastrowych.

%package -n bash-completion-drbd
Summary:	bash-completion for drbd
Summary(pl.UTF-8):	Bashowe uzupełnianie poleceń dla drbd
Group:		Applications/Shells
Requires:	bash-completion
BuildArch:	noarch

%description -n bash-completion-drbd
This package provides bash-completion for drbd.

%description -n bash-completion-drbd -l pl.UTF-8
Ten pakiet dostarcza bashowe uzupełnianie poleceń dla drbd.

%package -n drbd-xen
Summary:	Xen block device management script for DRBD
Summary(pl.UTF-8):	Skrypt zarządzający urządzeniem blokowym Xen dla DRBD
Group:		Applications/System
Requires:	drbd-utils = %{version}-%{release}
Requires:	xen

%description -n drbd-xen
This package contains a Xen block device helper script for DRBD,
capable of promoting and demoting DRBD resources as necessary.

%description -n drbd-xen -l pl.UTF-8
Ten pakiet zawiera pomocniczy skrypt urządzenia blokowego Xen dla
DRBD, potrafiący w razie potrzeby promować i degradować zasoby DRBD.

%prep
%setup -q
%patch0 -p1

# make constistent with configure settings (DRBD_RUN_DIR)
%{__sed} -i -e 's, /run/, /var/run/,' scripts/drbd.tmpfiles.conf

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%configure \
	--with-bashcompletion \
	--with-initscripttype=systemd \
	--with-pacemaker \
	--with-udev \
	--with-xen

%{__make} tools \
	KVER=dummy \
	CC="%{__cc}" \
	OPTCFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/sbin,%{_mandir}/man{5,8},%{_sysconfdir}} \
$RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d \
	$RPM_BUILD_ROOT/var/lib/drbd

%{__make} install \
	DRBD_ENABLE_UDEV=1 \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 60 haclient

%post
export NORESTART="yes"
%systemd_post drbd.service

%preun
%systemd_preun drbd.service

%postun
if [ "$1" = "0" ]; then
	%groupremove haclient
fi
%systemd_reload

%files
%defattr(644,root,root,755)
# symlinks
/sbin/drbdadm
/sbin/drbdmeta
/sbin/drbdsetup
%attr(755,root,root) %{_sbindir}/drbdadm
%attr(755,root,root) %{_sbindir}/drbdmon
%attr(4754,root,haclient) %{_sbindir}/drbdmeta
%attr(4754,root,haclient) %{_sbindir}/drbdsetup
%dir /lib/drbd
%attr(4754,root,haclient) /lib/drbd/drbdadm-*
%attr(4754,root,haclient) /lib/drbd/drbdsetup-*
%dir /lib/drbd/scripts
%attr(755,root,root) /lib/drbd/scripts/drbd
%attr(755,root,root) /lib/drbd/scripts/drbd-service-shim.sh
%attr(755,root,root) /lib/drbd/scripts/drbd-wait-promotable.sh
/lib/udev/rules.d/65-drbd.rules
%dir %{_prefix}/lib/drbd
%attr(755,root,root) %{_prefix}/lib/drbd/*
%dir %{_sysconfdir}/drbd.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/drbd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/drbd.d/global_common.conf
%{systemdunitdir}/drbd.service
%{systemdunitdir}/drbd-demote-or-escalate@.service
%{systemdunitdir}/drbd-graceful-shutdown.service
%{systemdunitdir}/drbd-lvchange@.service
%{systemdunitdir}/drbd-promote@.service
%{systemdunitdir}/drbd-reconfigure-suspend-or-error@.service
%{systemdunitdir}/drbd-services@.target
%{systemdunitdir}/drbd-wait-promotable@.service
%{systemdunitdir}/drbd@.service
%{systemdunitdir}/drbd@.target
%{systemdtmpfilesdir}/drbd.conf
%attr(750,root,root) %dir /var/lib/drbd
%attr(700,root,root) %dir /var/run/drbd
%{_mandir}/man5/drbd.conf.5*
%{_mandir}/man5/drbd.conf-8.3.5*
%{_mandir}/man5/drbd.conf-8.4.5*
%{_mandir}/man5/drbd.conf-9.0.5*
%{_mandir}/man7/drbd.service.7*
%{_mandir}/man7/drbd-lvchange@.service.7*
%{_mandir}/man7/drbd-promote@.service.7*
%{_mandir}/man7/drbd-reconfigure-suspend-or-error@.service.7*
%{_mandir}/man7/drbd-services@.target.7*
%{_mandir}/man7/drbd-wait-promotable@.service.7*
%{_mandir}/man7/drbd@.service.7*
%{_mandir}/man7/drbd@.target.7*
%{_mandir}/man8/drbd.8*
%{_mandir}/man8/drbd-8.3.8*
%{_mandir}/man8/drbd-8.4.8*
%{_mandir}/man8/drbd-9.0.8*
%{_mandir}/man8/drbdadm.8*
%{_mandir}/man8/drbdadm-8.3.8*
%{_mandir}/man8/drbdadm-8.4.8*
%{_mandir}/man8/drbdadm-9.0.8*
%{_mandir}/man8/drbddisk-8.3.8*
%{_mandir}/man8/drbddisk-8.4.8*
%{_mandir}/man8/drbdmeta.8*
%{_mandir}/man8/drbdmeta-8.3.8*
%{_mandir}/man8/drbdmeta-8.4.8*
%{_mandir}/man8/drbdmeta-9.0.8*
%{_mandir}/man8/drbdmon.8*
%{_mandir}/man8/drbdmon-9.0.8*
%{_mandir}/man8/drbdsetup.8*
%{_mandir}/man8/drbdsetup-8.3.8*
%{_mandir}/man8/drbdsetup-8.4.8*
%{_mandir}/man8/drbdsetup-9.0.8*
%lang(ja) %{_mandir}/ja/man5/drbd.conf.5*
%lang(ja) %{_mandir}/ja/man5/drbd.conf-8.4.5*
%lang(ja) %{_mandir}/ja/man5/drbd.conf-9.0.5*
%lang(ja) %{_mandir}/ja/man8/drbd.8*
%lang(ja) %{_mandir}/ja/man8/drbd-8.4.8*
%lang(ja) %{_mandir}/ja/man8/drbd-9.0.8*
%lang(ja) %{_mandir}/ja/man8/drbdadm.8*
%lang(ja) %{_mandir}/ja/man8/drbdadm-8.4.8*
%lang(ja) %{_mandir}/ja/man8/drbdadm-9.0.8*
%lang(ja) %{_mandir}/ja/man8/drbddisk-8.4.8*
%lang(ja) %{_mandir}/ja/man8/drbdmeta.8*
%lang(ja) %{_mandir}/ja/man8/drbdmeta-8.4.8*
%lang(ja) %{_mandir}/ja/man8/drbdmeta-9.0.8*
%lang(ja) %{_mandir}/ja/man8/drbdmon.8*
%lang(ja) %{_mandir}/ja/man8/drbdmon-9.0.8*
%lang(ja) %{_mandir}/ja/man8/drbdsetup.8*
%lang(ja) %{_mandir}/ja/man8/drbdsetup-8.4.8*
%lang(ja) %{_mandir}/ja/man8/drbdsetup-9.0.8*

%files -n resource-agents-drbd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/drbddisk
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/drbdupper
%attr(755,root,root) /lib/drbd/scripts/ocf.ra.wrapper.sh
%dir %{_prefix}/lib/ocf/resource.d/linbit
%attr(755,root,root) %{_prefix}/lib/ocf/resource.d/linbit/*
%{systemdunitdir}/ocf.ra@.service
%{_mandir}/man7/ocf.ra@.service.7*
%{_mandir}/man7/ocf_linbit_drbd.7*
%{_mandir}/man7/ocf_linbit_drbd-attr.7*

%files -n bash-completion-drbd
%defattr(644,root,root,755)
/etc/bash_completion.d/drbdadm

%files -n drbd-xen
%defattr(644,root,root,755)
%{_sysconfdir}/xen/scripts/block-drbd

# TODO: multipath subpackage? (R: multipath-tools)
#%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/multipath/conf.d/drbd.conf
